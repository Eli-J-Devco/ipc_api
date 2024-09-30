from dataclasses import asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from async_db.wrapper import async_db_request_handler

from src.utils.register_block.register_block_model import  RegisterBlockOutput,RegisterBlock
from src.configs.query_sql.register_block import query_all as register_block_query


class RegisterBlockService:
    def __init__(self,session: AsyncSession, **kwargs
                    ):
        self.session=session
    @async_db_request_handler
    async def get_register_blocks(self, id_template: int):
        try:
            register_block_list=[]
            query =register_block_query.select_register_block.format(id_template=id_template)
            result = await self.session.execute(text(query))
            register_blocks = [row._asdict() for row in result.all()]
            if not register_blocks:
                return []
            for template in register_blocks:
                register_block_list.append(RegisterBlock(**template))
        except Exception as e:
            print("Error get_register_blocks: ", e)
            return [] 
        finally:
            await self.session.close()
            return RegisterBlockOutput(registerblock=register_block_list)  