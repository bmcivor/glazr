class OrderError(Exception):
    """Base for anything the order service rejects."""


class DonutNotFound(OrderError):
    pass


class DonutUnavailable(OrderError):
    pass


class InvalidQuantity(OrderError):
    pass


class InvalidOrder(OrderError):
    pass


class InvalidStatusChange(OrderError):
    pass
