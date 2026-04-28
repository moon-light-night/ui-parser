from itertools import count

from fastapi import APIRouter, HTTPException, status

from app.models import Item, ItemCreate

router = APIRouter()

# Временное хранилище
items_db: list[Item] = []
item_id_counter = count(1)


def _get_item_index(item_id: int) -> int:
    for index, item in enumerate(items_db):
        if item.id == item_id:
            return index

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with id {item_id} not found",
    )


@router.get("/items", response_model=list[Item])
async def get_items() -> list[Item]:
    """Получить все элементы"""
    return items_db


@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int) -> Item:
    """Получить элемент по ID"""
    return items_db[_get_item_index(item_id)]


@router.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate) -> Item:
    """Создать новый элемент"""
    new_item = Item(id=next(item_id_counter), **item.model_dump())
    items_db.append(new_item)
    return new_item


@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemCreate) -> Item:
    """Обновить элемент"""
    item_index = _get_item_index(item_id)
    updated_item = Item(id=item_id, **item_update.model_dump())
    items_db[item_index] = updated_item
    return updated_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> None:
    """Удалить элемент"""
    items_db.pop(_get_item_index(item_id))
