- b1 : access link : https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNp10ltvgjAUAOC_0vRZ_wBL9jDxDg6FPRUfKhyhCRTTy5LF-N9Xj1TngrxAOd-5tOmZFl0JNKCV4qeaZOFbLol7pizeZhlJQX2LAvZkPH4nM5bagy6UOAAxHUGQdSdR6P0taYZsziad1LaFm4hBa16BN3M0C7bgsmyeSS8WKJZsooAb8EESwnUSEnUVCT-e6OoFjZMkG_Jr77PavUshK5JYXZPUcGP1LQMr9FlrzIqYL__KRehihsVCbrg_pT6-xPiGLaUGZciUF7Uf9ap7tUH16VUktBlQK1SJ3wl26zPuu03QbNnXqbwbIR_xLcZ3Q53w6P602yFNh0b_T1Ok2b3rQzlAR7QF1XJRuit3vibk1NTQQk4D91nCkdvG5DSXF0e5NV36IwsaGGVhRFVnq5oGR95ot7LYIBTcXd22_3v5BebH3qs 
- b2 : pass code.
graph TD;
    E[MQTT Service] --> F[Subscribe to MQTT Topics]
    F --> G[Consume MQTT Messages]
    G --> H[Handle MQTT Message]
    H --> I[Create Message Device Log DB]
    H --> J[Create Message Device MPPT Log DB]
    N --> K[Create Threading Push Status Log Device]
    K --> L[Message Status Log Device]
    O --> L[Message Status Log Device]
    L --> M[Push Data to MQTT]
    I --> N[Insert List Device Data]
    N --> O[Insert Each Device Data]
    J --> P[Create Data Insert DB]
    P --> Q1[data_device_mptt]
    P --> Q[data_device_mptt_string]
    Q --> R[updateDeviceMPPTString]
    Q1 --> S[updateDeviceMPPT]
- b3 : Diagram explanation:
Start MQTT Service: Starts the MQTT service, which initializes settings and configurations.
LogDevice Instance: Creates an instance of the LogDevice class, which stores data and processes messages.
Project Setup Config: Gets project configuration values.
Time Interval Log Device: Gets the logging interval for the device.
MQTT Service: Initializes the MQTT service with information such as host, port, username, password.
Subscribe to MQTT Topics: Subscribe to MQTT topics to receive messages.
Consume MQTT Messages: Consume messages from MQTT.
Handle MQTT Message: Handle MQTT messages.
Create Message Device Log DB: Creates device log messages to save to the database.
Create Message Device MPPT Log DB: Creates log messages for MPPT devices.
Create Threading Push Status Log Device: Creates tasks to push device log status to MQTT.
Message Status Log Device: Send device log status to MQTT.
Push Data to MQTT: Push data to MQTT.
Insert Each Device Data: Insert data for each device into the database.
Insert List Device Data: Insert a list of device data into the database.
Create Data Insert DB: Create data to insert into the database for MPPT devices.
Update Data in DB: Update data into the database.
Insert List Device MPPT Data: Insert a list of MPPT data into the database.
Insert Each Device MPPT Data: Insert data for each MPPT device.
Update Device MPPT: Update information for MPPT devices.