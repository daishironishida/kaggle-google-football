from kaggle_environments.envs.football.helpers import *
import math

GOAL_COORDS_SELF = (-1, 0)
GOAL_COORDS_OPPOSITION = (1, 0)

SHOOT_THRESH_X = 0.7
SHOOT_THRESH_Y = 0.20

GOALIE_CHARGE_THRESH = 0.01
GOALIE_CHARGE_SHOOT_THRESH = 0.5

DEFEND_TARGET_OFFSET = 0.05

GOALIE_IDX = 0

BALL_SPEED_FACTOR = 1

MARK_DISTANCE_THRESH = 0.1

@human_readable_agent
def agent(obs):

    ###### HELPER FUNCTIONS ######

    # Get distance
    def distance(pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    # Make sure player is sprinting
    def sprint(action, velocity):
        # Change direction first
        if get_movement_direction_from_vec(velocity) != action:
            if Action.Sprint in obs['sticky_actions']:
                return Action.ReleaseSprint
            else:
                return action
        # Start sprinting
        if Action.Sprint not in obs['sticky_actions']:
            return Action.Sprint
        else:
            return action
    
    # Shoot
    def shoot(pos):
        # Turn toward goal
        action = get_movement_direction(GOAL_COORDS_OPPOSITION, pos)

        # Change direction first
        if action not in obs['sticky_actions']:
            if Action.Sprint in obs['sticky_actions']:
                return Action.ReleaseSprint
            else:
                return action
        # Shoot
        return Action.Shot

    # Directions blocked by opposition
    def get_blocked_directions(pos):
        directions = set()
        for opposition in obs['right_team']:
            if distance(pos, opposition) < MARK_DISTANCE_THRESH:
                directions.add(get_movement_direction(opposition, pos))
        return directions

    # Get goalside of the ball
    def get_goalside_position(pos):
        ratio = DEFEND_TARGET_OFFSET / distance(pos, GOAL_COORDS_SELF)
        return (1 - ratio) * pos[0] - ratio, (1 - ratio) * pos[1]

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

    # Calculate appropriate movement direction from two positions
    def get_movement_direction(pos0, pos1):
        return get_movement_direction_from_vec((pos0[0] - pos1[0], pos0[1] - pos1[1]))

    # Calculate appropriate movement direction from vector
    def get_movement_direction_from_vec(vec):
        angle = get_degree(vec[0], vec[1])
        return Action(((angle + 202.5) // 45) % 8 + 1)

    # Get position of opponent's goalie
    def goalie_is_charging():
        return obs['right_team_direction'][GOALIE_IDX][0] < -GOALIE_CHARGE_THRESH

    ###### EVALUATE POSITION ######

    controlled_player_pos = obs['left_team'][obs['active']]
    controlled_player_vel = obs['left_team_direction'][obs['active']]

    ###### IN POSSESSION ######

    if obs['ball_owned_player'] == obs['active'] and obs['ball_owned_team'] == 0:

        # Shoot if goalie is off the line
        if controlled_player_pos[0] > GOALIE_CHARGE_SHOOT_THRESH \
            and abs(controlled_player_pos[1]) < SHOOT_THRESH_Y \
                and goalie_is_charging():

            return shoot(controlled_player_pos)

        # When player reaches the byline
        if controlled_player_pos[0] > SHOOT_THRESH_X:

            # Shot if player is close to the goal
            if abs(controlled_player_pos[1]) < SHOOT_THRESH_Y:
                return shoot(controlled_player_pos)
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

        # Check if opposition is in front of player
        if Action.Right in get_blocked_directions(controlled_player_pos):
            # Pass the ball
            return Action.ShortPass

        # Run towards the goal otherwise.
        return sprint(Action.Right, controlled_player_vel)

    ###### OUT OF POSSESSION ######

    # estimate future position of ball
    ball_target = (
        obs['ball'][0] + obs['ball_direction'][0] * BALL_SPEED_FACTOR,
        obs['ball'][1] + obs['ball_direction'][1] * BALL_SPEED_FACTOR
    )

    if obs['ball_owned_team'] == 1:
        # get goalside of the ball
        defend_target = get_goalside_position(ball_target)
    else:
        # run towards the ball
        defend_target = ball_target

    direction = get_movement_direction(defend_target, controlled_player_pos)
    return sprint(direction, controlled_player_vel)