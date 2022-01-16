# -*- coding: utf-8 -*-
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
import time
import ast
import random
import json


class IgracBot(Agent):
    class UpravljajPikulama(CyclicBehaviour):
        brojPikula = 0
        randomBroj = 0
        paranNeparan = 0

        async def generirajBrojPikula(self):
            self.randomBroj = random.randint(1,self.brojPikula)

        async def generirajParanNeparan(self):
            self.paranNeparan = random.randint(0,1)

        async def run(self):
            msg = await self.receive(timeout=100)
            print("Bot Štef je primio poruku")
            if msg:
                metadata = json.dumps(msg.metadata["ontology"])
                brojPikula = int(msg.body)

                if(metadata == '"pocetnoStanje"'):
                    print("Postavljam početno stanje Štefu...")
                    self.brojPikula = brojPikula
                    time.sleep(1)

                if(metadata == '"smanjiPikule"'):
                    print("Smanjujem pikule Štefu...")
                    self.brojPikula = self.brojPikula - brojPikula

                    msg_send = spade.message.Message(to="primatelj@rec.foi.hr",
                                            body="0",
                                            metadata={"ontology":"Smanjio sam pikule"})
                    time.sleep(1)
                    await self.send(msg_send)

                if(metadata == '"paranNeparan"'):
                    print("Racunam paran ili neparan kod Štefa...")
                    await self.generirajParanNeparan()
                    time.sleep(1)
                    msg_send = spade.message.Message(to="primatelj@rec.foi.hr",
                                                    body=f"{self.paranNeparan}")
                    await self.send(msg_send)

                
                if(metadata == '"povecajPikule"'):
                    print("Povecavam pikule Štefu...")
                    self.brojPikula = self.brojPikula + brojPikula

                    msg_send = spade.message.Message(to="primatelj@rec.foi.hr",
                                            body="0",
                                            metadata={"ontology":"Povecao sam pikule"})
                    time.sleep(1)
                    await self.send(msg_send)
                
                if(metadata == '"izracun"'):
                    print("Izracunavam pikule za Štefa...")
                    self.brojPikula = brojPikula
                    await self.generirajBrojPikula()
                    time.sleep(1)
                    msg_send = spade.message.Message(to="primatelj@rec.foi.hr",
                                                    body=f"{self.randomBroj}")
                    await self.send(msg_send)


    async def on_end(self):
            print("Gasim Štefa...")
            
    async def setup(self):
        print("Bot Štef: Pokrećem se!")
        ponasanje = self.UpravljajPikulama()               
        self.add_behaviour(ponasanje)


class Igrac(Agent):
    class UpravljajPikulama(CyclicBehaviour):
        brojPikula = 0

        async def run(self):
            msg = await self.receive(timeout=20)
            if msg:
                metadata = json.dumps(msg.metadata["ontology"])
                brojPikula = int(msg.body)

                if(metadata == '"pocetnoStanje"'):
                    print("Postavljam pocetno stanje igraču...")
                    self.brojPikula = brojPikula
                    msg_send = spade.message.Message(to="primatelj@rec.foi.hr",
                                            body="Pikule su postavljene")
                    time.sleep(1)
                    await self.send(msg_send)

                if(metadata == '"smanjiPikule"'):
                    print("Smanjujem pikule igraču...")
                    self.brojPikula = self.brojPikula - brojPikula
                    msg_send = spade.message.Message(to="primatelj@rec.foi.hr",
                                            body="0",
                                            metadata={"ontology":"Smanjio sam pikule"})
                    time.sleep(1)
                    await self.send(msg_send)
                
                if(metadata == '"povecajPikule"'):
                    print("Povečavam pikule igraču...")
                    self.brojPikula = self.brojPikula + brojPikula
                    msg_send = spade.message.Message(to="primatelj@rec.foi.hr",
                                            body="0",
                                            metadata={"ontology":"Povecao sam pikule"})
                    time.sleep(1)
                    await self.send(msg_send)
              

    async def on_end(self):
            print("Gasim igrača...")
            
    async def setup(self):
        print("Agent igrača: Pokrećem se!")
        ponasanje = self.UpravljajPikulama()
        self.add_behaviour(ponasanje)



class Klijent(Agent):
    class UnosFormule(CyclicBehaviour):
        brojPikulaIgraca = 0
        brojPikulaBota = 0
        imeIgraca = ""
        brojIzabranihPikulaBota = 0
        igracJeNaRedu = True
        botJeNaRedu = False

        async def posaljiPorukuBotu(self,msg,ontology):
            msg_send_bot = spade.message.Message(to="posiljatelj@rec.foi.hr",
                                            body=f"{msg}",
                                            metadata={"ontology":f"{ontology}"}
                                            ) 
            await self.send(msg_send_bot)
            msg = await self.receive(timeout=100)
            self.brojIzabranihPikulaBota = int(msg.body)

        async def posaljiPorukuIgracu(self,msg,ontology):
            msg_send_igrac = spade.message.Message(to="mlehpamer@rec.foi.hr",
                                            body=f"{msg}",
                                            metadata={"ontology":f"{ontology}"}
                                            ) 
            await self.send(msg_send_igrac)
            msg = await self.receive(timeout=100)


        async def upravljajIgracevimPogadanjem(self,ulazIgraca,pokusaj):
            print("Štef je odabrao: " + str(self.brojIzabranihPikulaBota))
            time.sleep(2)
            if (((pokusaj == "P" or pokusaj == "p") and (self.brojIzabranihPikulaBota % 2 == 0)) #Kada je korisnik pogodio
                or ((pokusaj == "N" or pokusaj == "n") and (self.brojIzabranihPikulaBota % 2 != 0))):
                self.brojPikulaBota = self.brojPikulaBota - ulazIgraca
                self.brojPikulaIgraca = self.brojPikulaIgraca + ulazIgraca
                await self.posaljiPorukuBotu(str(ulazIgraca),"smanjiPikule")
                await self.posaljiPorukuIgracu(str(ulazIgraca),"povecajPikule")
                self.igracJeNaRedu = True
                self.botJeNaRedu = False
            else:
                self.brojPikulaIgraca = self.brojPikulaIgraca - self.brojIzabranihPikulaBota
                self.brojPikulaBota = self.brojPikulaBota + self.brojIzabranihPikulaBota
                await self.posaljiPorukuBotu(str(self.brojIzabranihPikulaBota),"povecajPikule")
                await self.posaljiPorukuIgracu(str(self.brojIzabranihPikulaBota),"smanjiPikule")
                self.botJeNaRedu = True
                self.igracJeNaRedu = False

        async def upravljajBotovimPogadanjem(self,ulazIgraca,pokusaj):
            print("Štef je odabrao da vi imate " +pokusaj)
            time.sleep(2)
            print("Štef je odabrao " + str(self.brojIzabranihPikulaBota))
            time.sleep(2)
        
            if (((pokusaj == "P" or pokusaj == "p") and (ulazIgraca % 2 == 0)) or ((pokusaj == "N" or pokusaj == "n") and (ulazIgraca % 2 != 0))):
                self.brojPikulaBota = self.brojPikulaBota + self.brojIzabranihPikulaBota
                self.brojPikulaIgraca = self.brojPikulaIgraca - self.brojIzabranihPikulaBota
                await self.posaljiPorukuBotu(str(self.brojIzabranihPikulaBota),"povecajPikule")
                await self.posaljiPorukuIgracu(str(self.brojIzabranihPikulaBota),"smanjiPikule")
                self.botJeNaRedu = True
                self.igracJeNaRedu = False
            else:
                self.brojPikulaIgraca = self.brojPikulaIgraca + ulazIgraca
                self.brojPikulaBota = self.brojPikulaBota - ulazIgraca
                await self.posaljiPorukuBotu(str(ulazIgraca),"smanjiPikule")
                await self.posaljiPorukuIgracu(str(ulazIgraca),"povecajPikule")
                self.botJeNaRedu = False
                self.igracJeNaRedu = True

        async def run(self):
            time.sleep(5)

            print("========================DOBRODOŠLI U IGRU PIKULIRANJA========================================")
            print("PRAVILA IGRE:")
            print("1. Korak: Odabrati početno stanje pikula svakog igrača.")
            print("2. Korak: Izabrati koliko pikula želite uložiti.")
            print("3. Korak: Onaj koji je na redu za pogađanje pogađa koliko je drugi igrač uložio pikula tj. jel taj broj paran ili neparan.")
            print("4. Korak: Svatko pokazuje svoje pikule.")
            print("5. Korak Ako je osoba koja je pogađala broj pikula protivnika bila u pravu uzima onoliko pikula koliko je osoba koja pogađa uložila.")
            print("6. Korak Ako je osoba koja je pogađala broj pikula protivnika bila u krivu daje protivniku onoliko pikula koliko je protivnik uložio.")
            print("7. Korak Onaj koji je uzeo pikule je na redu za pogađanje.")
            print("8. Korak Igra se nastavlja sve dok netko ne ostane bez svih pikula.")
            print("============================================================================================")
            self.imeIgraca  = input("Molimo unesite svoje ime: ")
            brojPikulaZaigranje = input("Unesite broj pikula s kojima želite početi: ")
            self.brojPikulaBota = int(brojPikulaZaigranje)
            self.brojPikulaIgraca = int(brojPikulaZaigranje) 
            print("============================================================================================")
            print("=================================POČETNO STANJE IGRAČA=======================================")
            print(f"{self.imeIgraca} {self.brojPikulaIgraca}")
            print(f"Bot Štef: {self.brojPikulaBota}")

            msg_send_bot = spade.message.Message(to="posiljatelj@rec.foi.hr",
                                            body=f"{brojPikulaZaigranje}",
                                            metadata={"ontology":"pocetnoStanje"}
                                            ) 
            msg_send_igrac = spade.message.Message(to="mlehpamer@rec.foi.hr",
                                            body=f"{brojPikulaZaigranje}",
                                            metadata={"ontology":"pocetnoStanje"}
                                            ) 
            for x in range (0,6):
               b = "Ucitavanje "+ "."*x
               print(b,end="\r")
               time.sleep(1)            
            
            await self.send(msg_send_igrac)
            msg2 = await self.receive(timeout=10)
            await self.send(msg_send_bot)
            msg1 = await self.receive(timeout=10)


            while ((self.brojPikulaIgraca > 0) and (self.brojPikulaBota > 0)):
                print("=================================TRENUTNO STANJE IGRAČA=======================================")
                print(f"{self.imeIgraca} {self.brojPikulaIgraca}")
                print(f"Bot Štef: {self.brojPikulaBota}")
                ulazIgraca = input("Odaberite koliko pikula želite uložiti: ")
                ulazIgraca = int(ulazIgraca)
                if(int(ulazIgraca) > int(self.brojPikulaIgraca)):
                    print("Broj pikula za odabir ne može bit veći nego što imate pikula!")
                else:
                    pokusaj = ""
                    if(self.igracJeNaRedu):
                        print("BotŠtef je na redu da izabere broj pikula...")
                        await self.posaljiPorukuBotu(self.brojPikulaBota,"izracun")
                        pokusaj = input("Pogodite da li je BotŠtef izabrao paran ili neparan broj pikula (P/N)")
                        await self.upravljajIgracevimPogadanjem(ulazIgraca,pokusaj)
                    if(self.botJeNaRedu):
                        print("=================================TRENUTNO STANJE IGRAČA=======================================")
                        print(f"{self.imeIgraca} {self.brojPikulaIgraca}")
                        print(f"Bot Štef: {self.brojPikulaBota}")
                        ulazIgraca = input("Odaberite koliko pikula želite uložiti: ")
                        ulazIgraca = int(ulazIgraca)
                        if(int(ulazIgraca) > int(self.brojPikulaIgraca)):
                            print("Broj pikula za odabir ne može bit veći nego što imate pikula!")
                        print("Pričekajte da BotŠtef odabere da li ste odabrali paran ili neparan broj")
                        await self.posaljiPorukuBotu(0,"paranNeparan")
                        if(self.brojIzabranihPikulaBota == 1):
                            pokusaj  = "P"
                        else:
                            pokusaj = "N"                           
                        await self.posaljiPorukuBotu(self.brojPikulaBota,"izracun")  
                        time.sleep(1)
                        await self.upravljajBotovimPogadanjem(ulazIgraca,pokusaj)
            if(self.brojPikulaBota > 0):
                print("Čestitamo, ali ne vama. BotŠtef je pobijedio")
            if(self.brojPikulaIgraca > 0):
                print("Čestitamo, pobijedili ste")
            ulaz = input("Upisite broj 9 za kraj igre ili bilo koju tipku za ponovnu igru: ")
            if(ulaz == "9"):
                exit()

    async def setup(self):
        print("KlijentAgent: Pokrećem se!")
        ponasanje = self.UnosFormule()
        izracun = spade.template.Template(
            metadata={"ontology":"izracun"})      
        self.add_behaviour(ponasanje)

if __name__ == '__main__':
    Klijent = Klijent("primatelj@rec.foi.hr","tajna")
    Klijent.start()

    IgracBot = IgracBot("posiljatelj@rec.foi.hr","tajna")
    IgracBot.start()

    Igrac = Igrac("mlehpamer@rec.foi.hr","ipeg1627")
    Igrac.start()

    time.sleep(10)
    while Klijent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            Klijent.stop()
            break
    IgracBot.stop()
    Klijent.stop()
    Igrac.stop()
    spade.quit_spade() 
