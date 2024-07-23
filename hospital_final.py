import threading
import time
import concurrent.futures
import random
import mysql.connector
import matplotlib.pyplot as plt  
import csv
import os

cnx = mysql.connector.connect(user='root', password='xxxx',
                host='xxxxx')

cursor = cnx.cursor()
cursor.execute("DROP DATABASE hospital")
cnx.commit()

cursor.execute("CREATE DATABASE hospital")
cnx.commit()

cursor.close()
cnx.close()

cnx = mysql.connector.connect(user='root', password='xxxxx',
                host='xxxxx',
                database='hospital')
cursor = cnx.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS og_patients (
        number INT AUTO_INCREMENT PRIMARY KEY,
        id INT,
        disease VARCHAR(255)
    );
""")
cnx.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients_emer (
        number INT AUTO_INCREMENT PRIMARY KEY,
        id INT,
        disease VARCHAR(255),
        severity INT
    );
""")
cnx.commit()


class Hospital():
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Hospital, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()

    def run(self):
        self.lock.acquire()
        print(f"Hospital is opening")
        time.sleep(30)
        self.lock.release()
        time.sleep(.2)
        print(f"Hospital closed")

class MasterQueues():
    def __init__(self):
        super().__init__()
        self.queue = []
        self.lock = threading.Lock()

    def add_person(self,student):
        with self.lock:
            self.queue.append(student)

    def remove_person(self,student):
        if self.person_in_queue(student):
            with self.lock:
                return self.queue.remove(student)
        return None

    def get_first_person(self):
        with self.lock:
            if(len(self.queue) > 0):
                return self.queue.pop()
            else:
                return None 
    
    def person_in_queue(self,student):
        with self.lock:
            decision = True if student in self.queue else False
        return decision

    def is_my_queue_empty(self):
        with self.lock:
            empty = len(self.queue) == 0
        return empty


my_queues = {"availableDocs":MasterQueues(), "availableNurses":MasterQueues(),
            "radiologyQueue":MasterQueues(), "consultancyQueue":MasterQueues(),
            "heartQueue":MasterQueues(), "receptionQueue":MasterQueues(),
            "emerQueue":MasterQueues(), "emerPrioQueue":MasterQueues()}


class Doctor():
    def __init__(self, my_queues, id):
        super().__init__()
        self.id = id
        self.hospital = Hospital()
        self.my_queues = my_queues
        self.lock = threading.Lock()

    def run(self):
        hospital_open = True
        while self.hospital.lock.locked():
            if hospital_open== True:
                print(f"Doctor {self.id} started working")
                self.my_queues["availableDocs"].add_person(self)
                hospital_open = False
        else:
            time.sleep(.1)
            print(f"Doctor {self.id} stopped working")


class Nurse():  
    def __init__(self, my_queues, id):
        super().__init__()
        self.id = id
        self.hospital = Hospital()
        self.my_queues = my_queues
        self.lock = threading.Lock()


    def run(self):
        hospital_open = True
        while self.hospital.lock.locked():
            if hospital_open== True:
                print(f"Nurse {self.id} is working")
                self.my_queues["availableNurses"].add_person(self)
                hospital_open = False
        else:
            time.sleep(.1)
            print(f"Nurse {self.id} stopped working")
    

class Cardiology():
    def __init__(self, my_queues, id):
        super().__init__()
        self.my_queues = my_queues
        self.id = id
        self.patient_treat = []
        self.hospital = Hospital()
        self.lock = threading.Lock()

    def check_heart(self):
        while self.hospital.lock.locked():
            # Check if there are patients in the heart queue
            if len(self.my_queues["heartQueue"].queue):
                for doctor in range(len(self.my_queues["availableDocs"].queue)):
                    if not self.my_queues["availableDocs"].queue[doctor].lock.locked():
                        self.my_queues["availableDocs"].queue[doctor].lock.acquire()
                        self.lock.acquire()
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is coming to Cardiology room {self.id}")
                        self.patient_treat.append(self.my_queues["heartQueue"].queue[0])
                        self.my_queues['heartQueue'].remove_person(self.my_queues['heartQueue'].queue[0])
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is currently treating patient {self.patient_treat[0]['id']} in cardiology room {self.id}")
                        time.sleep(.5)
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is done treating patient {self.patient_treat[0]['id']}")
                        self.patient_treat.remove(self.patient_treat[0])
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is free again, as well as cardiology room {self.id}")
                        self.my_queues["availableDocs"].queue[doctor].lock.release()
                        self.lock.release()
                        break
                    else:
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is busy and can't come")
            else:
                print("No patients in Cardiology")
                time.sleep(.5)


class Radiology():
    def __init__(self, my_queues, id):
        super().__init__()
        self.my_queues = my_queues
        self.id = id
        self.hospital = Hospital()
        self.lock = threading.Lock()
        self.patient_treat = []

    def radiologyCheck(self):
        while self.hospital.lock.locked():
            if len(self.my_queues["radiologyQueue"].queue):
                for doctor in range(len(self.my_queues["availableDocs"].queue)):
                    if not self.my_queues["availableDocs"].queue[doctor].lock.locked():
                        self.my_queues["availableDocs"].queue[doctor].lock.acquire()
                        self.lock.acquire()
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is coming to Radiology room {self.id}")
                        self.patient_treat.append(self.my_queues["radiologyQueue"].queue[0])
                        self.my_queues['radiologyQueue'].remove_person(self.my_queues['radiologyQueue'].queue[0])
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is currently treating patient {self.patient_treat[0]['id']} in radiology room {self.id}")
                        time.sleep(.5)
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is done treating patient {self.patient_treat[0]['id']}")
                        self.patient_treat.remove(self.patient_treat[0])
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is free again, as well as radiology room {self.id}")
                        self.my_queues["availableDocs"].queue[doctor].lock.release()
                        self.lock.release()
                    else:
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is busy and can't come")
                break
            else:
                print("No patients in Radiology")
                time.sleep(.5)



class Consultancy():
    def __init__(self, my_queues, id):
        super().__init__()
        self.hospital = Hospital()
        self.my_queues = my_queues
        self.id = id
        self.patient_treat = []
        self.lock = threading.Lock()


    def check(self):
            while self.hospital.lock.locked():
                if len(self.my_queues["consultancyQueue"].queue):
                    for nurse in range(len(self.my_queues["availableNurses"].queue)):
                        if self.my_queues["availableNurses"].queue[nurse].lock.locked():
                            print(f"Nurse {self.my_queues['availableNurses'].queue[nurse].id} is busy and can't come to consult")
                        else:
                            self.my_queues["availableNurses"].queue[nurse].lock.acquire()
                            self.lock.acquire()
                            print(f"Nurse {self.my_queues['availableNurses'].queue[nurse].id} is coming to consultancy room {self.id}")
                            self.patient_treat.append(self.my_queues["consultancyQueue"].queue[0])
                            self.my_queues['consultancyQueue'].remove_person(self.my_queues['consultancyQueue'].queue[0])
                            self.consult()
                            print(f"Nurse {self.my_queues['availableNurses'].queue[nurse].id} is free again, as well as consultancy room {self.id}")
                            self.my_queues["availableNurses"].queue[nurse].lock.release()
                            self.lock.release()
                            break
                else:
                    print("No patients in consultancy")
                    time.sleep(.5)

    
    def consult(self):
        disease = random.choice(["broken bone", "heart problem"])
        if disease == "broken bone":
            self.patient_treat[0]["disease"] = disease
            time.sleep(.2)
            print(f'Patient {self.patient_treat[0]["id"]} has been diagnosed with a {self.patient_treat[0]["disease"]} and sent to Radiology')
            self.my_queues['radiologyQueue'].add_person(self.patient_treat[0])
            self.patient_treat.remove(self.patient_treat[0])
            return
             
        elif disease == "heart problem":
            self.patient_treat[0]["disease"] = disease
            time.sleep(.2)
            print(f'Patient {self.patient_treat[0]["id"]} has been diagnosed with a {self.patient_treat[0]["disease"]} and sent to heart doctor')
            self.my_queues['heartQueue'].add_person(self.patient_treat[0])
            self.patient_treat.remove(self.patient_treat[0])
            return


class Reception():
    def __init__(self, my_queues):
        super().__init__()
        self.hospital = Hospital()
        self.my_queues = my_queues
        self.lock = threading.Lock()
    
    def action(self):
        while self.hospital.lock.locked():
            if self.hospital.lock.locked() == False:
                break
            elif self.my_queues['receptionQueue'].is_my_queue_empty() == False:
                print(f"Receptionist is talking to patient {self.my_queues['receptionQueue'].queue[0]['id']}")
                time.sleep(.2)
                if self.my_queues['receptionQueue'].queue[0]["disease"] == "idk":
                    print(f'Patient {self.my_queues["receptionQueue"].queue[0]["id"]} has been sent to consultancy to find their problem')
                    self.my_queues['consultancyQueue'].add_person(self.my_queues['receptionQueue'].queue[0])
                    self.my_queues['receptionQueue'].remove_person(self.my_queues['receptionQueue'].queue[0])

                elif self.my_queues['receptionQueue'].queue[0]["disease"] == "broken bone":
                    print(f'Patient {self.my_queues["receptionQueue"].queue[0]["id"]} has been sent to radiology due to broken bone')
                    self.my_queues['radiologyQueue'].add_person(self.my_queues['receptionQueue'].queue[0])
                    self.my_queues['receptionQueue'].remove_person(self.my_queues['receptionQueue'].queue[0])

                elif self.my_queues['receptionQueue'].queue[0]["disease"] == "heart problem":
                    print(f'Patient {self.my_queues["receptionQueue"].queue[0]["id"]} has been sent to heart doctor due to heart problem')
                    self.my_queues['heartQueue'].add_person(self.my_queues['receptionQueue'].queue[0])
                    self.my_queues['receptionQueue'].remove_person(self.my_queues['receptionQueue'].queue[0])
            else:
                self.my_queues['receptionQueue'].lock.acquire()
                print("No patients in reception")
                self.my_queues['receptionQueue'].lock.release()
                time.sleep(.5)

                


class EmergencyRoom():
    def __init__(self, my_queues,id):
        super().__init__()
        self.hospital = Hospital()
        self.patient_treat = []
        self.id = id
        self.my_queues = my_queues
        self.lock = threading.Lock()

    def treat(self):
        while self.hospital.lock.locked():
            if len(self.my_queues["emerPrioQueue"].queue):
                for doctor in range(len(self.my_queues["availableDocs"].queue)):
                    if not self.my_queues["availableDocs"].queue[doctor].lock.locked():
                        self.my_queues["availableDocs"].queue[doctor].lock.acquire()
                        self.lock.acquire()
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is coming to Emergency Room {self.id}")
                        self.patient_treat.append(self.my_queues["emerPrioQueue"].queue[0])
                        self.my_queues['emerPrioQueue'].remove_person(self.my_queues['emerPrioQueue'].queue[0])
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is currently treating patient {self.patient_treat[0]['id']} in emergency room {self.id}")
                        time.sleep(.3)
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is done treating patient {self.patient_treat[0]['id']} with severity {self.patient_treat[0]['severity']}")
                        self.patient_treat.remove(self.patient_treat[0])
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is free again, as well as emergency room {self.id}")
                        self.my_queues["availableDocs"].queue[doctor].lock.release()
                        self.lock.release()
                        break
                    else:
                        print(f"Doctor {self.my_queues['availableDocs'].queue[doctor].id} is busy and can't come")
    
            elif len(self.my_queues["emerQueue"].queue):
                for nurse in range(len(self.my_queues["availableNurses"].queue)):
                    if not self.my_queues["availableNurses"].queue[nurse].lock.locked():
                        self.my_queues["availableNurses"].queue[nurse].lock.acquire()
                        self.lock.acquire()
                        print(f"Nurse {self.my_queues['availableNurses'].queue[nurse].id} is coming to Emergency Room {self.id}")
                        self.patient_treat.append(self.my_queues["emerQueue"].queue[0])
                        self.my_queues['emerQueue'].remove_person(self.my_queues['emerQueue'].queue[0])
                        print(f"Nurse {self.my_queues['availableNurses'].queue[nurse].id} is currently treating patient {self.patient_treat[0]['id']} in emergency room {self.id}")
                        time.sleep(.2)
                        print(f"Nurse {self.my_queues['availableNurses'].queue[nurse].id} is done treating patient {self.patient_treat[0]['id']} with severity {self.patient_treat[0]['severity']}")
                        self.patient_treat.remove(self.patient_treat[0])
                        print(f"Nurse {self.my_queues['availableNurses'].queue[nurse].id} is free again, as well as emergency room {self.id}")
                        self.my_queues["availableNurses"].queue[nurse].lock.release()
                        self.lock.release()
                        break
                    else:
                        print(f"Nurse {self.my_queues['availableNurses'].queue[nurse].id} is busy and can't come")
            else:
                print("No patients in Emergency room")
                time.sleep(.5)

def save_to_file_OG(self):
    with open('hospital_OG.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.id, self.disease])

def save_to_file_Emer(self):
    with open('emergency.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.id, self.disease, self.severity])

def save_to_db():
    with open('hospital_OG.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute("""
                INSERT INTO og_patients (id, disease)
                VALUES (%s, %s)
            """, (row[0], row[1]))
    cnx.commit()

    with open('emergency.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            cursor.execute("""
                INSERT INTO patients_emer (id, disease, severity)
                VALUES (%s, %s, %s)
            """, (row[0], row[1], row[2]))
    cnx.commit()

def delete_files():
    os.remove("hospital_OG.csv")
    os.remove("emergency.csv")
            

class Patients():
    def __init__(self, my_queues, id):
        super().__init__()
        self.id = id
        self.my_queues = my_queues
        self.lock = threading.Lock()
        self.emergency = random.choices(["Yes", "No"], weights=(.4, .6))[0]
        self.severity = random.choice([1,2,3,4])
        self.disease = random.choice(["broken bone", "idk", "heart problem"])

    def enter(self):
        self.lock.acquire()
        if self.emergency == "No":
            print(f"Patient {self.id} has entered the hospital")
            self.my_queues['receptionQueue'].add_person({"id": self.id, "disease": self.disease})
            save_to_file_OG(self)
            self.lock.release()
        else:
            if self.severity == 4:
                print(f"Patient {self.id} has entered the priority queue in emergency room with severity {self.severity}")
                self.my_queues['emerPrioQueue'].add_person({"id": self.id, "disease": self.disease, "severity":self.severity})
                save_to_file_Emer(self)
                self.lock.release()
            else:
                print(f"Patient {self.id} has entered the normal queue in emergency room with severity {self.severity}")
                self.my_queues['emerQueue'].add_person({"id": self.id, "disease": self.disease, "severity":self.severity})
                save_to_file_Emer(self)
                self.lock.release()



hospital = Hospital()
doctors = [Doctor(my_queues,x) for x in range(3)]
nurses = [Nurse(my_queues, x) for x in range(10)] 
cardiology = [Cardiology(my_queues, x) for x in range(2)]
radiology = [Radiology(my_queues, x) for x in range(2)]
consultancyRooms = [Consultancy(my_queues, x) for x in range(2)]
reception = Reception(my_queues)
emergencyroom = [EmergencyRoom(my_queues, x) for x in range(2)]

#ran = random.randint(25)
patients = [Patients(my_queues,x) for x in range(30)]

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    executor.submit(hospital.run)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor1:
        executor1.submit(reception.action)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor2:
            executor2.map(Consultancy.check, consultancyRooms)
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor3:
                executor3.map(Cardiology.check_heart, cardiology)
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor3:
                    executor3.map(Radiology.radiologyCheck, radiology)
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor4:
                        executor4.map(EmergencyRoom.treat, emergencyroom)
                        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor5:
                            executor5.map(Doctor.run, doctors)
                            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor6:
                                executor6.map(Nurse.run, nurses)
                                with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor7:
                                    executor7.map(Patients.enter, patients)

print("Reception queue: ", my_queues["receptionQueue"].queue)
print("Emergency room queue", my_queues["emerQueue"].queue)
print("Heart doc queue", my_queues["heartQueue"].queue)
print("Radiology queue", my_queues["radiologyQueue"].queue)
print("Consultancy queue", my_queues["consultancyQueue"].queue)


save_to_db()
delete_files()

## graph 1
counts = []
diseases = ["broken bone", "idk", 'heart problem']
cursor.execute("SELECT disease from og_patients")
result = cursor.fetchall()

broken_bone = result.count(('broken bone',))
idk = result.count(('idk',))
heart_problem = result.count(('heart problem',))

counts.append(broken_bone)
counts.append(idk)
counts.append(heart_problem)

plt.bar(diseases, counts, color=['yellow', 'blue', 'red'])
plt.title("Count of diseases of original hospital patients")
plt.show()


## graph 2
counts = []
diseases = ["broken bone", "idk", 'heart problem']
cursor.execute("SELECT disease from patients_emer")
result = cursor.fetchall()

broken_bone = result.count(('broken bone',))
idk = result.count(('idk',))
heart_problem = result.count(('heart problem',))

counts.append(broken_bone)
counts.append(idk)
counts.append(heart_problem)

plt.bar(diseases, counts, color=['yellow', 'blue', 'red'])
plt.title("Count of diseases of emergency patients")
plt.show()

## graph 3 
counts = []
severities = ["1", "2", "3", "4"]
cursor.execute("SELECT severity from patients_emer")
result = cursor.fetchall()

sever1 = result.count((1,))
sever2 = result.count((2,))
sever3 = result.count((3,))
sever4 = result.count((4,))

counts.append(sever1)
counts.append(sever2)
counts.append(sever3)
counts.append(sever4)


plt.bar(severities, counts, color=['yellow', 'blue', 'red', 'green'])
plt.title("Count of severities of emergency patients")
plt.show()

cursor.close()
cnx.close()
