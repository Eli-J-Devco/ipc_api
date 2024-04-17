from .template_model import Template
from .template_entity import Template as TemplateEntity
from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

@Injectable
class TemplateService:

    @async_db_request_handler
    async def add_template(self, template: Template, session: AsyncSession):
        new_template = TemplateEntity(
            **template.dict()
        )
        session.add(new_template)
        await session.commit()
        return new_template.id

    @async_db_request_handler
    async def get_template(self, session: AsyncSession):
        query = select(TemplateEntity)
        result = await session.execute(query)
        return result.scalars().all()
