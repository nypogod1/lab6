
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21
MIN_TOTAL = 0
COUPON_SAVE10 = {"code": "SAVE10", "discount_rate": 0.10}
COUPON_SAVE20 = {"code": "SAVE20", "discount_rate_high": 0.20, "discount_rate_low": 0.05, "threshold": 200}
COUPON_VIP = {"code": "VIP", "discount_high": 50, "discount_low": 10, "threshold": 100}
VALID_COUPONS = [COUPON_SAVE10, COUPON_SAVE20, COUPON_VIP]
def parse_request(request: dict):
    """Извлекаем данные из запроса"""
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency
def validate_request(user_id, items, currency):
    """Проверяем, что данные корректны"""
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items are required")

    if currency is None:
        currency = DEFAULT_CURRENCY
    
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")
    
    return currency


def calculate_subtotal(items):
    """Считаем общую сумму товаров"""
    subtotal = 0
    for item in items:
        subtotal += item["price"] * item["qty"]
    return subtotal


def calculate_discount(coupon, subtotal):
    """Считаем скидку по купону"""
    if coupon is None or coupon == "":
        return 0
    coupon_data = None
    for valid_coupon in VALID_COUPONS:
        if valid_coupon["code"] == coupon:
            coupon_data = valid_coupon
            break
    
    if coupon_data is None:
        raise ValueError("unknown coupon")
        
    if coupon == COUPON_SAVE10["code"]:
        return int(subtotal * COUPON_SAVE10["discount_rate"])
    
    elif coupon == COUPON_SAVE20["code"]:
        if subtotal >= COUPON_SAVE20["threshold"]:
            return int(subtotal * COUPON_SAVE20["discount_rate_high"])
        else:
            return int(subtotal * COUPON_SAVE20["discount_rate_low"])
    
    elif coupon == COUPON_VIP["code"]:
        if subtotal >= COUPON_VIP["threshold"]:
            return COUPON_VIP["discount_high"]
        else:
            return COUPON_VIP["discount_low"]
    
    return 0


def calculate_tax(amount):
    """Считаем налог"""
    return int(amount * TAX_RATE)


def generate_order_id(user_id, items_count):
    """Генерируем ID заказа"""
    return f"{user_id}-{items_count}-X"


def process_checkout(request: dict) -> dict:

    user_id, items, coupon, currency = parse_request(request)
    currency = validate_request(user_id, items, currency)
    
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(coupon, subtotal)
    
    total_after_discount = subtotal - discount
    if total_after_discount < MIN_TOTAL:
        total_after_discount = MIN_TOTAL
    
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax
    
    order_id = generate_order_id(user_id, len(items))

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
