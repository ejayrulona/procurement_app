from django.db import models

class Item(models.Model):
    class Category(models.TextChoices):
        GOODS = "goods", "Goods"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"
        CONSULTING_SERVICES = "consulting_services", "Consulting Services"


    class Unit(models.TextChoices):
        PIECE = "piece", "Piece"
        UNIT = "unit", "Unit"
        SET = "set", "Set"
        REAM = "ream", "Ream"
        BOX = "box", "Box"
        PACK = "pack", "Pack"
        BOTTLE = "bottle", "Bottle"
        ROLL = "roll", "Roll"
        METER = "meter", "Meter"
        LITER = "liter", "Liter"
        KILOGRAM = "kilogram", "Kilogram"
        BAG = "bag", "Bag"
        PAIR = "pair", "Pair"
        BUNDLE = "bundle", "Bundle"
        GALLON = "gallon", "Gallon"


    code = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=20, choices=Unit.choices)
    reorder_level = models.IntegerField()
    location = models.TextField()
    supplier = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ["-created_at"]


    def __str__(self):
        return self.name
    
    @property
    def stock_status(self):
        if self.quantity <= 0:
            return "Out of Stock"
        elif self.quantity <= self.reorder_level:
            return "Low Stock"
        
        return "In Stock"
    

class StockMovementLog(models.Model):
    class MovementType(models.TextChoices):
        STOCK_IN = "stock_in", "Stock In"
        STOCK_OUT = "stock_out", "Stock Out"
        ADJUSTMENT = "adjustment", "Adjustment"


    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="movement_logs")
    movement_type = models.CharField(max_length=10, choices=MovementType.choices)
    quantity_changed = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    remarks = models.TextField()
    performed_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="stock_movements")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} | {self.get_movement_type_display()} | Qty: {self.quantity_changed} | {self.created_at:%B %d, %Y %I:%M %p} | By: {self.performed_by}"