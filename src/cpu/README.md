- b1 : access link : https://mermaid-js.github.io/mermaid-live-editor/edit#pako:eNp10ltvgjAUAOC_0vRZ_wBL9jDxDg6FPRUfKhyhCRTTy5LF-N9Xj1TngrxAOd-5tOmZFl0JNKCV4qeaZOFbLol7pizeZhlJQX2LAvZkPH4nM5bagy6UOAAxHUGQdSdR6P0taYZsziad1LaFm4hBa16BN3M0C7bgsmyeSS8WKJZsooAb8EESwnUSEnUVCT-e6OoFjZMkG_Jr77PavUshK5JYXZPUcGP1LQMr9FlrzIqYL__KRehihsVCbrg_pT6-xPiGLaUGZciUF7Uf9ap7tUH16VUktBlQK1SJ3wl26zPuu03QbNnXqbwbIR_xLcZ3Q53w6P602yFNh0b_T1Ok2b3rQzlAR7QF1XJRuit3vibk1NTQQk4D91nCkdvG5DSXF0e5NV36IwsaGGVhRFVnq5oGR95ot7LYIBTcXd22_3v5BebH3qs 
- b2 : pass code.
graph TD;
    A[Main Function] -->|Initializes| B[MQTT Service]
    A -->|Sets up| C[AsyncIOScheduler]
    A -->|Runs in| P[Async Loop]
    C -->|Schedules| D[getIPCHardwareInformation]
    D -->|Collects data from| E[CPUInfo Class]

    E -->|Gets System Information| F[getSystemInformation]
    E -->|Gets Boot Time| G[getBootTime]
    E -->|Gets CPU Information| H[getCpuInformation]
    E -->|Gets Memory Information| I[getMemoryInformation]
    E -->|Gets Disk Information| J[getDiskInformation]
    E -->|Gets Network Information| K[getNetworkInformation]
    E -->|Gets Network Speed| L[getNetworkSpeedInformation]
    E -->|Gets Disk IO Information| M[getDiskIoInformation]

    F -->|Pushes data to| N[MQTT Topics]
    G -->|Pushes data to| N[MQTT Topics]
    H -->|Pushes data to| N[MQTT Topics]
    I -->|Pushes data to| N[MQTT Topics]
    J -->|Pushes data to| N[MQTT Topics]
    K -->|Pushes data to| N[MQTT Topics]
    L -->|Pushes data to| N[MQTT Topics]
    M -->|Pushes data to| N[MQTT Topics]

    N -->|Sends data| O[MQTT Broker]



