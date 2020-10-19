from kaggle_environments import make

env = make("football",
        debug=True,
        configuration={"save_video": True,
                        "scenario_name": "11_vs_11_kaggle",
                        "running_in_notebook": False,
                        'dump_full_episodes': False,
                        "render": False,
                        "logdir": "./logs"})

output = env.run(["src/submission.py", "src/submission.py"])[-1]