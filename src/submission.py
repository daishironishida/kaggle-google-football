from kaggle_environments.envs.football.helpers import *

SHOOT_THRESH_X = 0.4
SHOOT_THRESH_Y = 0.25

@human_readable_agent
def agent(obs):
    # Make sure player is running.
    if Action.Sprint not in obs['sticky_actions']:
        return Action.Sprint
    # We always control left team (observations and actions
    # are mirrored appropriately by the environment).
    controlled_player_pos = obs['left_team'][obs['active']]
    # Does the player we control have the ball?
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
                return Action.HighPass

        # Run towards the goal otherwise.
        return Action.Right
    else:
        # Run towards the ball.
        if obs['ball'][0] > controlled_player_pos[0] + 0.05:
            return Action.Right
        if obs['ball'][0] < controlled_player_pos[0] - 0.05:
            return Action.Left
        if obs['ball'][1] > controlled_player_pos[1] + 0.05:
            return Action.Bottom
        if obs['ball'][1] < controlled_player_pos[1] - 0.05:
            return Action.Top
        # Try to take over the ball if close to the ball.
        return Action.Slide