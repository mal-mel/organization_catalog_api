#!/usr/bin/env python3
import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.building import Building
from app.models.activity import Activity
from app.models.organization import Organization
from app.models.phone_number import PhoneNumber


def generate_phone_number():
    formats = [
        "###-##-##",
        "8-9##-###-##-##",
        "+7-9##-###-##-##",
        "8-4##-###-##-##"
    ]

    format_str = random.choice(formats)

    phone = ''.join(
        str(random.randint(0, 9)) if c == '#' else c
        for c in format_str
    )

    return phone


def seed():
    print("Starting database seeding...")
    db = SessionLocal()

    try:
        print("Cleaning existing data...")
        db.query(PhoneNumber).delete()
        db.query(Organization).delete()
        db.query(Building).delete()
        db.query(Activity).delete()
        db.commit()

        print("Creating buildings...")
        buildings_data = [
            {"address": "г. Москва, ул. Ленина 1, офис 3", "lat": 55.7558, "lon": 37.6173},
            {"address": "г. Москва, ул. Блюхера 32/1", "lat": 55.7600, "lon": 37.6200},
            {"address": "г. Москва, ул. Тверская 15", "lat": 55.7500, "lon": 37.6100},
            {"address": "г. Москва, ул. Арбат 25", "lat": 55.7495, "lon": 37.6060},
            {"address": "г. Москва, пр. Мира 10", "lat": 55.7800, "lon": 37.6300},

            {"address": "г. Санкт-Петербург, Невский пр. 50", "lat": 59.9343, "lon": 30.3351},
            {"address": "г. Санкт-Петербург, ул. Садовая 15", "lat": 59.9260, "lon": 30.3170},

            {"address": "г. Екатеринбург, ул. Ленина 25", "lat": 56.8380, "lon": 60.5970},
            {"address": "г. Екатеринбург, пр. Космонавтов 10", "lat": 56.8500, "lon": 60.6100},
        ]

        buildings = []
        for data in buildings_data:
            building = Building(
                address=data["address"],
                latitude=data["lat"],
                longitude=data["lon"]
            )
            buildings.append(building)

        db.add_all(buildings)
        db.flush()
        print(f"Created {len(buildings)} buildings")

        print("Creating activities tree...")

        food = Activity(name="Еда")
        automobiles = Activity(name="Автомобили")
        electronics = Activity(name="Электроника")
        clothing = Activity(name="Одежда")
        services = Activity(name="Услуги")

        meat = Activity(name="Мясная продукция", parent=food)
        dairy = Activity(name="Молочная продукция", parent=food)
        bakery = Activity(name="Хлебобулочные изделия", parent=food)
        beverages = Activity(name="Напитки", parent=food)

        beef = Activity(name="Говядина", parent=meat)
        pork = Activity(name="Свинина", parent=meat)
        chicken = Activity(name="Курица", parent=meat)
        cheese = Activity(name="Сыры", parent=dairy)
        milk = Activity(name="Молоко", parent=dairy)
        yogurt = Activity(name="Йогурты", parent=dairy)

        trucks = Activity(name="Грузовые", parent=automobiles)
        cars_light = Activity(name="Легковые", parent=automobiles)
        parts = Activity(name="Запчасти", parent=automobiles)
        accessories = Activity(name="Аксессуары", parent=automobiles)

        tires = Activity(name="Шины", parent=parts)
        brakes = Activity(name="Тормозные системы", parent=parts)
        engine_parts = Activity(name="Двигатель", parent=parts)

        computers = Activity(name="Компьютеры", parent=electronics)
        smartphones = Activity(name="Смартфоны", parent=electronics)
        home_appliances = Activity(name="Бытовая техника", parent=electronics)

        mens_clothing = Activity(name="Мужская одежда", parent=clothing)
        womens_clothing = Activity(name="Женская одежда", parent=clothing)
        children_clothing = Activity(name="Детская одежда", parent=clothing)

        legal = Activity(name="Юридические услуги", parent=services)
        consulting = Activity(name="Консалтинг", parent=services)
        education = Activity(name="Образование", parent=services)

        activities = [
            food, automobiles, electronics, clothing, services,
            meat, dairy, bakery, beverages,
            beef, pork, chicken, cheese, milk, yogurt,
            trucks, cars_light, parts, accessories,
            tires, brakes, engine_parts,
            computers, smartphones, home_appliances,
            mens_clothing, womens_clothing, children_clothing,
            legal, consulting, education
        ]

        db.add_all(activities)
        db.flush()
        print(f"Created {len(activities)} activities")

        print("Creating organizations...")
        organizations_data = [
            {
                "name": 'ООО "Рога и Копыта"',
                "building": buildings[0],
                "phones": 2,
                "activities": [meat, dairy, beef, pork]
            },
            {
                "name": 'ЗАО "Молочные реки"',
                "building": buildings[1],
                "phones": 1,
                "activities": [dairy, cheese, milk, yogurt]
            },
            {
                "name": 'ИП "Свежий хлеб"',
                "building": buildings[2],
                "phones": 1,
                "activities": [bakery]
            },
            {
                "name": 'ОАО "Мясной Двор"',
                "building": buildings[3],
                "phones": 3,
                "activities": [meat, chicken, beef]
            },

            {
                "name": 'ИП "АвтоМир"',
                "building": buildings[4],
                "phones": 2,
                "activities": [cars_light, parts, accessories]
            },
            {
                "name": 'ООО "ГрузовикСервис"',
                "building": buildings[5],
                "phones": 1,
                "activities": [trucks, parts, tires, brakes]
            },
            {
                "name": 'ЗАО "АвтоДеталь"',
                "building": buildings[6],
                "phones": 2,
                "activities": [parts, engine_parts, brakes]
            },

            {
                "name": 'ООО "ТехноМир"',
                "building": buildings[7],
                "phones": 3,
                "activities": [electronics, computers, smartphones]
            },
            {
                "name": 'ИП "БытоваяТехника"',
                "building": buildings[8],
                "phones": 1,
                "activities": [home_appliances]
            },

            {
                "name": 'ООО "Правовед"',
                "building": buildings[0],
                "phones": 2,
                "activities": [legal, consulting]
            },
            {
                "name": 'ИП "БизнесКонсалт"',
                "building": buildings[1],
                "phones": 1,
                "activities": [consulting]
            },
        ]

        organizations = []
        for data in organizations_data:
            phone_numbers = [
                PhoneNumber(number=generate_phone_number())
                for _ in range(data["phones"])
            ]

            organization = Organization(
                name=data["name"],
                building=data["building"],
                phone_numbers=phone_numbers,
                activities=data["activities"]
            )
            organizations.append(organization)

        db.add_all(organizations)
        db.commit()

        print(f"✅ Database seeding completed successfully!")
        print(f"📊 Statistics:")
        print(f"   - Buildings: {len(buildings)}")
        print(f"   - Activities: {len(activities)}")
        print(f"   - Organizations: {len(organizations)}")

        total_phones = sum(len(org.phone_numbers) for org in organizations)
        print(f"   - Phone numbers: {total_phones}")

        print(f"🌍 Data is ready for use!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during database seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()