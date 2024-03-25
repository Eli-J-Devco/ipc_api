# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
#----------------------------------------
# /**
# 	 * @description take time 
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {}
# 	 * @return datetime
# 	 */
def get_utc():
    now=None
    try:
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if now:
            return now
    except Exception as err:
        return None