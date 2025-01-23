from RoboflowPython import roboflow
import os
#from notebook import notebookapp
import webbrowser

rf = roboflow.Roboflow(api_key="")
project = rf.workspace().project("scouting-2024")
model = project.version("1").model

job_id, signed_url, expire_time = model.predict_video(
    "video.mp4",
    #add the file path to your chosen video
    fps=20,
    prediction_type="batch-video",
)

results = model.poll_until_video_results(job_id)

print(results)
# roboflow.login()



# jupyter_server = list(notebookapp.list_running_servers())[0]["url"]
# webbrowser.open(jupyter_server + "notebooks/create-models.ipynb")
# # create a project
# rf.create_project(
#     project_name="Scouting 2024",
#     project_type="project-type",
#     license="project-license" # "private" for private projects
# )

# workspace = rf.workspace("Scouting 2024")
# project = workspace.project("aj-oj2mu").download("yolov8")
# version = project.version("8.3.59")

# # upload a dataset
# project.upload_dataset(
#     dataset_path="./dataset/",
#     num_workers=10,
#     dataset_format="yolov8", # supports yolov8, yolov5, and Pascal VOC
#     project_license="MIT",
#     project_type="object-detection"
# )

# # upload model weights
# version.deploy(model_type="yolov8", model_path=f"{HOME}/runs/detect/train/")

# # run inference
# model = version.model

# img_url = "https://media.roboflow.com/quickstart/aerial_drone.jpeg"

# predictions = model.predict(img_url, hosted=True).json()

# print(predictions)
