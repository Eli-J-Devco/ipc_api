- b1 : access link : https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNp10ltvgjAUAOC_0vRZ_wBL9jDxDg6FPRUfKhyhCRTTy5LF-N9Xj1TngrxAOd-5tOmZFl0JNKCV4qeaZOFbLol7pizeZhlJQX2LAvZkPH4nM5bagy6UOAAxHUGQdSdR6P0taYZsziad1LaFm4hBa16BN3M0C7bgsmyeSS8WKJZsooAb8EESwnUSEnUVCT-e6OoFjZMkG_Jr77PavUshK5JYXZPUcGP1LQMr9FlrzIqYL__KRehihsVCbrg_pT6-xPiGLaUGZciUF7Uf9ap7tUH16VUktBlQK1SJ3wl26zPuu03QbNnXqbwbIR_xLcZ3Q53w6P602yFNh0b_T1Ok2b3rQzlAR7QF1XJRuit3vibk1NTQQk4D91nCkdvG5DSXF0e5NV36IwsaGGVhRFVnq5oGR95ot7LYIBTcXd22_3v5BebH3qs 
- b2 : pass code.
graph TD;
    A[Main Function] -->|Initializes| B[MQTT Service]
    A -->|Sets up| C[AsyncIOScheduler]
    A -->|Gets IdChannel| D[Command Line Argument]
    A -->|Gets type of file| O[get_type_of_file]

    B -->|Subscribes to topics| E[subscribe_to_mqtt_topics]
    E -->|Consumes messages| G[consume_mqtt_messages]
    G -->|Handles message| H[LogFile Class]

    H -->|Creates log file| I[create_file_log]
    I -->|Creates message| Q[create_message]
    
    Q -->|Creates and writes file| L[create_and_write_file]
    L -->|Create Directory Path| M[create_directory_path]
    M -->|Writes data to file| N[write_data_to_file]
    N -->|insert_data_table_synced| P[insert_data_table_synced]
    P -->|Creates topic| Y[create_topic]
    Y -->|Pushes status log| K[push_status_log_file]
    A -->|Runs in| R[Async Loop]
