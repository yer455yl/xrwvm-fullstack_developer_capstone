from django.core.management.base import BaseCommand
from djangoapp.models import CarMake, CarModel

class Command(BaseCommand):
    help = "Populate car makes and models without replacing existing data"
    def handle(self, *args, **options):
        for make, model, kind in [("Toyota","Camry","Sedan"),("Toyota","RAV4","SUV"),("Honda","Accord","Sedan"),("Honda","CR-V","SUV"),("Ford","Mustang","Coupe"),("Ford","F-150","Truck"),("Tesla","Model 3","Sedan"),("BMW","X3","SUV")]:
            brand,_ = CarMake.objects.get_or_create(name=make,defaults={"description": f"{make} vehicles"})
            CarModel.objects.get_or_create(car_make=brand,name=model,year=2023,defaults={"type":kind})
        self.stdout.write(self.style.SUCCESS("Car inventory ready"))
