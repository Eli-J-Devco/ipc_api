# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        'src.app_module:http_server',
        host="0.0.0.0",
        port=3002,
        reload=True
    )
    
