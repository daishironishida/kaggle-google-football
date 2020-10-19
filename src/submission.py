from kaggle_environments.envs.football.helpers import *
import math

SHOOT_THRESH_X = 0.7
SHOOT_THRESH_Y = 0.25

DEFEND_TARGET_OFFSET = 0.05

# Make sure player is sprinting
def sprint(obs, action):
    # Change direction first
    if action not in obs['sticky_actions']:
        return action
    # Start sprinting
    if Action.Sprint not in obs['sticky_actions']:
        return Action.Sprint
    else:
        return Action.Idle

# Get goalside of the ball
def get_goalside_position(x, y):
    ratio = DEFEND_TARGET_OFFSET / math.sqrt((x+1) ** 2 + y ** 2)
    return (1 - ratio) * x - ratio, (1 - ratio) * y

# Calculate angle in degrees
# @return angle between -180 and 180
def get_degree(x, y):
    if x == 0:
        return 90 if y > 0 else -90
    base = math.atan(y / x) * 180 / math.pi

    if x > 0:
        return base
    if y >= 0:
        return base + 180
    else:
        return base - 180

# Calculate appropriate movement direction
def get_movement_direction(x, y):
    angle = get_degree(x, y)
    return Action(((angle + 202.5) // 45) % 8 + 1)

@human_readable_agent
def agent(obs):

    controlled_player_pos = obs['left_team'][obs['active']]

    ###### IN POSSESSION ######

    if obs['ball_owned_player'] == obs['active'] and obs['ball_owned_team'] == 0:

        # When player reaches the byline
        if controlled_player_pos[0] > SHOOT_THRESH_X:

            # Shot if player is close to the goal
            if abs(controlled_player_pos[1]) < SHOOT_THRESH_Y:
                return Action.Shot
            # Cross if player is far from the goal
            else:
                # Stop sprinting
                if Action.Sprint in obs['sticky_actions']:
                    return Action.ReleaseSprint
                # Turn toward goal
                if Action.Right in obs['sticky_actions']:
                    return Action.Top if controlled_player_pos[1] > 0 else Action.Bottom
                # Cross into the box
                return Action.ShortPass

        # Run towards the goal otherwise.
        return sprint(obs, Action.Right)

    ###### OUT OF POSSESSION ######

    if obs['ball_owned_team'] == 1:
        # get goalside of the ball
        defend_target = get_goalside_position(obs['ball'][0], obs['ball'][1])
    else:
        #run towards the ball
        defend_target = (obs['ball'][0], obs['ball'][1])

    direction = get_movement_direction(
        defend_target[0] - controlled_player_pos[0],
        defend_target[1] - controlled_player_pos[1]
    )
    return sprint(obs, direction)