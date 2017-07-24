class Animal:
    def __init__(self, age, weight):
        self.__age = age
        self.__weight = weight
    def speak(self):
        print(self.__age)
        print(self.__weight)
    def fight(self):
        pass
    def getAge(self):
        return self.__age

class swim:
    def __init__(self, speed):
        self.speed = speed
    def swim(self):
        print("I can swim")

class dog(Animal, swim):
    def __init__(self, age, weight):
        super().__init__(age, weight)
    def speak(self):
        super().speak()
        print("this is dog")
    def fight(self):
        print("fight")

class cat(Animal, swim):
    def __init__(self, age, weight):
        Animal.__init__(self, age, weight)
    def speak(self):
        super().speak()
        print("this is cat")

ddd = dog(12,15)
ddd.speak()
ddd.swim()
ddd.fight()
print(ddd.getAge())
print("-"*20)
ccc = cat(1,2)
ccc.speak()
ccc.swim()
ccc.fight()
