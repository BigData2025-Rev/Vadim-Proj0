import csv
import os
import mysql.connector
import pandas as pd


class catalogue():
    

    file_name = "default.csv"
    fieldnames = ["Name", "Type", "DamageType", "Damage", "Penetration", "FireRate", "MagazineSize", "ReloadSpeed", "Special"]
    searchable_fieldnames = ["name", "type", "damagetype", "damage", "penetration", "firerate", "magazinesize", "reloadspeed", "special"]

    cnx = mysql.connector.connect(user='root', password='1234', host='localhost', database='proj0')
    cursor = cnx.cursor()

    #initialize and create file
    def __init__ (self, file_name):
        self.file_name = file_name
        if os.path.isfile(file_name) == False:
            self.create_file()
        print("The siege upon Managed Democracy continues. Let us rally to her defense.")

    #create file and add fieldnames
    def create_file(self):
        file = open(self.file_name, "w", newline='')
        writer = csv.DictWriter(file, fieldnames=catalogue.fieldnames)
        writer.writeheader()
        file.close()
        catalogue.cursor.execute("CREATE TABLE IF NOT EXISTS Projectiles (Name varchar(255) PRIMARY KEY, DemolitionForce int, StaggerForce int,PushForce int);")
        catalogue.cnx.commit()
        catalogue.cursor.execute("CREATE TABLE IF NOT EXISTS Weapons(Name varchar(255) PRIMARY KEY, Type varchar(255), DamageType varchar(255), Damage int, Penetration int,  FireRate int, MagazineSize int, ReloadTime float, Special varchar(255), Projectile varchar(255), FOREIGN KEY (Projectile) REFERENCES Projectiles(Name));")
        catalogue.cnx.commit()

    #update weapon by searching for record, modifying the list, deleting the record, and readding it
    def update_weapon(self, name, field, new_val):
        if field.lower() in catalogue.searchable_fieldnames:
            try:
                record = self.search_weapon(name)
                record_index = catalogue.searchable_fieldnames.index(field.lower())
                record[record_index] = new_val
                self._remove_from_weapon_from_csv(record[0])
                self._readd_weapon(record)
                self.update_weapon_db(record[0], catalogue.fieldnames[record_index], new_val)
                print("Weapon updated successfully")
            except:
                print("No weapon matching this description found")
        else:
            print("Invalid field to alter")
    
    #update the database
    def update_weapon_db(self, name, field, new_val):
        try:
            query_data = [new_val, name]
            query = 'UPDATE Weapons SET {} = %s WHERE Name = %s ;'
            catalogue.cursor.execute(query.format(field), query_data)
            catalogue.cnx.commit()
        except:
            raise Exception("Failed to update weapon in database.")

    #private method to append updated record back into csv
    def _readd_weapon(self, weapon):
        try:
            file = open(self.file_name, "a", newline='')
            writer = csv.writer(file)
            writer.writerow(weapon)
            file.close()
        except:
            raise Exception("Invalid file name try again")

    #append csv file with new weapon
    def add_weapon(self, weapon_list, projectile_name):
        try:
            file = open(self.file_name, "a", newline='')
            writer = csv.writer(file)
            writer.writerow(weapon_list)
            file.close()
            self.add_weapon_to_db(weapon_list, projectile_name)
            print("Weapon added successfully")
        except:
            print("Invalid file name or invalid parameter inputs. Try again")
    
    #insert new weapon to Weapons table
    def add_weapon_to_db(self, weapon_list, projectile_name):
        weapon_list.append(projectile_name)
        query = "INSERT INTO Weapons VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        catalogue.cursor.execute(query, (weapon_list))
        catalogue.cnx.commit()
    
    #insert new projectile into Projectiles table
    def add_projectile(self, projectile_info):
        try:
            query = "INSERT INTO Projectiles VALUES (%s, %s, %s, %s);"
            catalogue.cursor.execute(query, (projectile_info))
            catalogue.cnx.commit()
        except:
            print("Faield to add projectile.")
    
    #update projectile in Projectiles table
    def update_projectile(self, name, attribute, new_val):
        try:
            query_data = [new_val, name]
            query = 'UPDATE Projectiles SET {} = %s WHERE Name = %s ;'
            catalogue.cursor.execute(query.format(attribute), (query_data))
            catalogue.cnx.commit()
        except:
            print("Failed to update projectile")

    def remove_weapon_from_db(self, weapon_name):
        query = "DELETE FROM Weapons WHERE Name = %s;"
        catalogue.cursor.execute(query, (weapon_name,))
        catalogue.cnx.commit()
    
    # private method to remove weapon only from csv as normal remove also removes it from db
    def _remove_from_weapon_from_csv(self, weapon_name):
        try:
            weapon_name = weapon_name.lower()
            temp_file_name = "temp.csv"
            file_r = open(self.file_name, "r")
            file_w = open(temp_file_name, 'w+', newline='')
            writer = csv.writer(file_w)
            for record in csv.reader(file_r):
                if weapon_name not in record[0].lower():
                    writer.writerow(record)
            file_w.close()
            file_r.close()
            os.remove(self.file_name)
            os.rename(temp_file_name, self.file_name)
        except:
            raise Exception("Invalid file name try again")
    
    # remove weapon from both csv and Weapons table
    def remove_weapon(self, weapon_name):
        try:
            full_name = weapon_name
            weapon_name = weapon_name.lower()
            temp_file_name = "temp.csv"
            file_r = open(self.file_name, "r")
            file_w = open(temp_file_name, 'w+', newline='')
            writer = csv.writer(file_w)
            for record in csv.reader(file_r):
                if weapon_name not in record[0].lower():
                    writer.writerow(record)
                else:
                    full_name = record[0]
            file_w.close()
            file_r.close()
            self.remove_weapon_from_db(full_name)
            os.remove(self.file_name)
            os.rename(temp_file_name, self.file_name)
            print("Weapon removed successfully")
        except:
            print("Invalid file name try again")
    
    # go through csv until found record containing search
    def search_weapon(self, weapon):
        try:
            file = open(self.file_name, "r")
            for record in csv.reader(file):
                if weapon in record[0].lower():
                    return record
            file.close()
            return "No weapon matching this description found"
        except:
            return "Invalid file name try again"

    # go through csv until found chosen attribute with searched value
    def search_by_attribute(self, search_val, attribute):
        if attribute in catalogue.searchable_fieldnames:
            try:
                weapons = []
                record_index = catalogue.searchable_fieldnames.index(attribute)
                file = open(self.file_name, "r")
                for record in csv.reader(file):
                    if search_val in record[record_index].lower():
                        weapons.append(record)
                file.close()
                return weapons
            except:
                return "Invalid attribute try again"
        else: 
            return "Invalid attribute try again"
    
    # join select to find all weapons that have the same projectile
    def search_by_projectile(self, caliber):
        query = """SELECT Weapons.Name, Type, DamageType, Damage, Penetration, FireRate, MagazineSize, ReloadTime, 
        Special, DemolitionForce, StaggerForce, PushForce FROM Weapons INNER JOIN Projectiles ON Weapons.Projectile = Projectiles.Name WHERE Weapons.Projectile = %s ;"""
        catalogue.cursor.execute(query, (caliber,))
        return catalogue.cursor.fetchall()
    
    # take all results and print it to look more legible
    def formatted_print(self, weapon_list_to_print):
        if len(weapon_list_to_print) == 0 or type(weapon_list_to_print) == str:
            print("Nothing to print")
            return
        if type(weapon_list_to_print[0]) != list and type(weapon_list_to_print[0]) != tuple:
            weapon_list_to_print = [weapon_list_to_print]
        df = pd.DataFrame(weapon_list_to_print, columns=catalogue.fieldnames)
        print(df)
    
    def detailed_print(self, weapon_list_to_print):
        if len(weapon_list_to_print) == 0 or type(weapon_list_to_print) == str:
            print("Nothing to print")
            return
        if type(weapon_list_to_print[0]) != list and type(weapon_list_to_print[0]) != tuple:
            weapon_list_to_print = [weapon_list_to_print]
        print_fields = catalogue.fieldnames + ["Demolition Force", "Stagger Force", "Push Force"]
        df = pd.DataFrame(weapon_list_to_print, columns=print_fields)
        print(df)

    def close(self):
        print("Go now, and fear the shadow of neither death, nor tyranny; for justice is our cause")
        self.cursor.close()
        self.cnx.close()
        exit()


arsenal = catalogue("default.csv")

while True:
    answer = input("Select an action: search, update, add, remove, or exit: ")
    answer = answer.lower()
    if answer == "search":
        search_type = input("Search either by Name, Type, Penetration, Special, Projectile: ")
        search_type = search_type.lower()
        if search_type == "name":
            search_name = input("Weapon name: ").lower()
            results = arsenal.search_weapon(search_name)
            arsenal.formatted_print(results)
        elif search_type == "projectile":
            projectile = input("Full projectile name: ")
            arsenal.detailed_print(arsenal.search_by_projectile(projectile))
        elif search_type in arsenal.searchable_fieldnames:
            search = input("Attribute value: ")
            arsenal.formatted_print(arsenal.search_by_attribute(search.lower(), search_type))
    elif answer == "update":
        update_field = input("Are you updating a weapon or projectile? ")
        update_field = update_field.lower()
        if update_field == "weapon":
            name = input("Weapon name:").lower()
            attribute = input("Select field to update: Name, Penetration, Damage, Damage Type, FireRate, MagazineSize, ReloadSpeed, Special: ").lower()
            new_val = input("New value: ")
            if attribute in arsenal.searchable_fieldnames:
                arsenal.update_weapon(name, attribute, new_val)
        elif update_field == "projectile":
            name = input("Full projectile name: ").lower()
            attribute = input("Select field to update: DemolitionForce, StaggerForce, PushForce: ")
            new_val = input("New value: ")
            arsenal.update_projectile(name, attribute, new_val)
    elif answer == "add":
        name = input("Name: ")
        weapon_type = input("Type: ")
        damage_type = input("Damage type: ")
        damage = input("Damage: ")
        pen = input("Penetration value: ")
        fire_rate = input("Fire Rate: ")
        mag = input("Magazine capacity: ")
        reload = input("Full reload time: ")
        special = input("Special attributes: ")
        weapon_list = [name, weapon_type, damage_type, damage, pen, fire_rate, mag, reload, special]
        projectile_check = input("Does this weapon use an existing projectile (Y/N)? ")
        projectile_name = input("Full projectile name: ")
        if projectile_check.lower() == "n":
            demo_force = input("Demolition force: ")
            stagger = input("Stagger force: ")
            push = input("Push force: ")
            projectile_data = [projectile_name, demo_force, stagger, push]
            arsenal.add_projectile(projectile_data)
        arsenal.add_weapon(weapon_list, projectile_name)
    elif answer == "remove":
        weapon = input("Name of weapon to remove: ")
        arsenal.remove_weapon(weapon)
    elif answer == "exit" or answer == "quit":
        arsenal.close()
    else:
        print("Invalid input")
