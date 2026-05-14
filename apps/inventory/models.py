from django.db import models

class ObjectOfExpenditure(models.Model):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Object of Expenditure"
        verbose_name_plural = "Object of Expenditures"
        ordering = ["name"]


    def __str__(self):
        return self.name


class ObjectCode(models.Model):
    code = models.CharField(max_length=30)
    expenditure = models.ForeignKey(ObjectOfExpenditure, on_delete=models.PROTECT, related_name="object_codes")

    class Meta:
        verbose_name = "Object Code"
        verbose_name_plural = "Object Codes"
        ordering = ["code"]


    def __str__(self):
        return f"{self.code} - {self.expenditure}"


class ItemCode(models.Model):
    code = models.CharField(max_length=30)
    general_description = models.CharField(max_length=150)
    object_code = models.ForeignKey(ObjectCode, on_delete=models.PROTECT, related_name="item_codes")

    class Meta:
        verbose_name  = "Item Code"
        verbose_name_plural = "Item Codes"
        ordering = ["code"]

    
    def __str__(self):
        return f"{self.code} - {self.general_description}"
    

class Item(models.Model):
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
        LOT = "lot", "Lot"
        PAD = "pad", "Pad"
        TUBE = "tube", "Tube"
        SACHET = "sachet", "Sachet"
        TANK = "tank", "Tank"
        TIN = "tin", "Tin"
        BAR = "bar", "Bar"
        DOZEN = "dozen", "Dozen"


    name = models.CharField(max_length=100)
    specification = models.CharField(max_length=100, null=True, blank=True)
    unit = models.CharField(max_length=20, choices=Unit.choices)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)

    # might add quantity later
    # quantity will be computed in the following:
    # it starts at 0 and annually resets to 0
    # all approved items from all ppmp will be added to quantity of that item record

    item_code = models.ForeignKey(ItemCode, on_delete=models.PROTECT, related_name="item_records")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ["-created_at"]


    def __str__(self):
        return self.name