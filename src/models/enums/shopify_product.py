import enum


class ProductStatus(enum.Enum):
    active = "active"
    publish = "publish"
    archived = "archived"
    draft = "draft"
    pending = "pending"
    private = "private"
    future = "future"
