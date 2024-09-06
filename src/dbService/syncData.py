# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from entity.sync_data.sync_data_entity import *

class SyncDataService:
    @staticmethod
    async def insert_sync_data(session: AsyncSession, data_list: list):
        try:
            # Tạo danh sách các từ điển cho từng bản ghi
            records = [
                {
                    'id': entry[0],  # Thêm id nếu cần thiết
                    'id_device': entry[1],
                    'modbusdevice': entry[2],
                    'ensuredir': entry[3],
                    'source': entry[4],
                    'filename': entry[5],
                    'createtime': entry[6],
                    'data': entry[7],  # Đảm bảo đúng thứ tự
                    'id_upload_channel': entry[8]  # Thay đổi chỉ số cho đúng
                }
                for entry in data_list
            ]

            # Thực hiện chèn nhiều bản ghi
            query = insert(SyncData).values(records)
            result = await session.execute(query)

            # Lưu thay đổi vào cơ sở dữ liệu
            await session.commit()
            print("Sync data successfully --->")
            return result.rowcount  # Trả về số lượng bản ghi đã chèn
        except Exception as e:
            print(f"Error: '{e}'")
            await session.rollback()  # Hoàn tác nếu có lỗi
            return None
        finally:
            await session.close()