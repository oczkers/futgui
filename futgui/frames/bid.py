import tkinter as tk
from frames.base import Base
import multiprocessing as mp
import queue
import time
from PIL import Image, ImageTk
from core.playercard import create
from core.bid import bid

class Bid(Base):
    def __init__(self, master, controller):
        Base.__init__(self, master, controller)

        self._bidding = False
        self._bidCycle = 0
        self._errorCount = 0
        self._banWait = 0
        self._startTime = 0
        self.auctionsWon = 0
        self.sold = 0

        options = tk.Frame(self, bg='#1d93ab')
        options.grid(column=0, row=0, sticky='ns')

        self.text = tk.Text(self, bg='#1d93ab', fg='#ffeb7e', bd=0)
        self.text.grid(column=1, row=0, sticky='news')
        self.q = mp.Queue()
        self.p = None

        self.maxBid = tk.StringVar()
        self.sell = tk.StringVar()
        self.binPrice = tk.StringVar()
        self.minCredits = tk.StringVar()
        self.minCredits.set(1000)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        back = tk.Button(options, bg='#1d93ab', text='Back to Player Search', command=self.playersearch)
        back.grid(column=0, row=0, sticky='we')

        self.card = tk.Label(options, bg='#1d93ab')
        self.card.grid(column=0, row=1)

        form = tk.Frame(options, padx=15, pady=15)
        form.grid(column=0, row=2, sticky='ns')

        options.grid_columnconfigure(0, weight=1)
        options.grid_rowconfigure(0, weight=0)
        options.grid_rowconfigure(1, weight=0)
        options.grid_rowconfigure(2, weight=1)

        watchBtn = tk.Button(form, text='Watch Player', command=self.watch)
        watchBtn.grid(column=0, row=0, columnspan=2, padx=5, pady=5)

        maxLbl = tk.Label(form, text='Max Bid:')
        maxLbl.grid(column=0, row=1, sticky='e')
        maxEntry = tk.Entry(form, width=8, textvariable=self.maxBid)
        maxEntry.grid(column=1, row=1, sticky='w')

        sellLbl = tk.Label(form, text='Sell For:')
        sellLbl.grid(column=0, row=2, sticky='e')
        sellEntry = tk.Entry(form, width=8, textvariable=self.sell)
        sellEntry.grid(column=1, row=2, sticky='w')

        binPriceLbl = tk.Label(form, text='BIN:')
        binPriceLbl.grid(column=0, row=3, sticky='e')
        binPriceEntry = tk.Entry(form, width=8, textvariable=self.binPrice)
        binPriceEntry.grid(column=1, row=3, sticky='w')

        minCreditsLbl = tk.Label(form, text='Min Credits:')
        minCreditsLbl.grid(column=0, row=4, sticky='e')
        minCreditsEntry = tk.Entry(form, width=8, textvariable=self.minCredits)
        minCreditsEntry.grid(column=1, row=4, sticky='w')

        self.bidbtn = tk.Button(form, text='Start Bidding', command=self.start)
        self.bidbtn.grid(column=0, row=5, columnspan=2, padx=5, pady=5)

        self.checkQueue()
        self.clearErrors()

    def watch(self):
        self.controller.show_frame(Watch, player=self.args['player'])

    def bid(self):
        if not self._bidding:
            return
        if self.p is not None and self.p.is_alive():
            self.after(5000, self.bid)
            return
        # Populate trades with what I am already watching
        trades = {}
        try:
            for item in self.controller.api.watchlist():
                trades[item['tradeId']] = item['resourceId']
            self._bidding = True
            self._bidCycle += 1
            self.p = mp.Process(target=bid, args=(
                self.q,
                self.controller.api,
                int(self.args['player']['id']),
                int(self.maxBid.get()),
                int(self.sell.get()),
                int(self.binPrice.get()),
                int(self.minCredits.get()),
                trades
                ))
            self.p.start()
            self.controller.status.set_credits(self.controller.api.credits)
            self.after(5000, self.bid)
        except ExpiredSession:
            self.stop()
            self.controller.show_frame(Login)
        except (FutError, RequestException) as e:
            self.updateLog('%s    %s: %s (%s)\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), type(e).__name__, e.reason, e.code))
            self._errorCount += 1
            if self._errorCount >= 3:
                self.stop()
            else:
                self.after(5000, self.bid)
            pass

    def checkResult(self, r):
        self.updateLog('%s    Checking Result...\n' % (time.strftime('%Y-%m-%d %H:%M:%S')))
        if r.ready():
            self.updateLog('%s    Result Success!\n' % (time.strftime('%Y-%m-%d %H:%M:%S')))
            self.bid()
        else:
            self.updateLog('%s    Still waiting...\n' % (time.strftime('%Y-%m-%d %H:%M:%S')))
            self.after(500, self.checkResult, (r,))

    def start(self):
        if not self._bidding and self.controller.api is not None:
            self._bidding = True
            self._bidCycle = 0
            self._errorCount = 0
            self._startTime = time.time()
            self.bidbtn.config(text='STOP Bidding', command=self.stop)
            self.update_idletasks()
            self.updateLog('%s    Started bidding...\n' % (time.strftime('%Y-%m-%d %H:%M:%S')))
            self.bid()

    def stop(self):
        if self._bidding:
            self._bidding = False
            self._bidCycle = 0
            self._errorCount = 0
            self.controller.status.set_status('Setting bid options for %s...' % self.displayName)
            self.bidbtn.config(text='Start Bidding', command=self.start)
            self.update_idletasks()
            self.updateLog('%s    Stopped bidding...\n' % (time.strftime('%Y-%m-%d %H:%M:%S')))

    def checkQueue(self):
        try:
            msg = self.q.get(False)
            if isinstance(msg, FutError):
                self.updateLog('%s    %s: %s (%s)\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), type(msg).__name__, msg.reason, msg.code))
                self._errorCount += 1
                if self._errorCount >= 3:
                    self._banWait = self._banWait + 1
                    self.updateLog('%s    Too many errors. Will resume in %d minutes...\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), self._banWait*5))
                    self.stop()
                    login = self.controller.get_frame(Login)
                    login.logout(switchFrame=False)
                    self.after(self._banWait*5*60000, self.relogin, (login))
            elif not isinstance(msg, str):
                self.auctionsWon += msg[0]
                self.sold += msg[1]
                self.controller.status.set_stats((self.auctionsWon, self.sold))
                self.controller.status.set_status('Bidding on %s: %d' % (self.displayName, self._bidCycle))
                if time.time() - self._startTime > 18000:
                    self.updateLog('%s    Pausing to prevent ban... Will resume in 1 hour...\n' % (time.strftime('%Y-%m-%d %H:%M:%S')))
                    self.stop()
                    login = self.controller.get_frame(Login)
                    login.logout(switchFrame=False)
                    self.after(60*60000, self.relogin, (login))
            else:
                self._banWait = 0
                self.updateLog(msg)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.checkQueue)

    def relogin(self, login):
        login.login(switchFrame=False)
        self.start()

    def clearErrors(self):
        if self._bidding and self._errorCount > 0:
            self._errorCount = self._errorCount - 1
        self.after(900000, self.clearErrors)

    def updateLog(self, msg):
        self.text.insert('end',msg)
        self.text.see(tk.END)
        self.update_idletasks()

    def playersearch(self):
        self.stop()
        self.controller.show_frame(PlayerSearch)

    def active(self):
        if self.controller.api is None:
            self.controller.show_frame(Login)

        Base.active(self)
        self.text.delete(1.0, tk.END)
        self.displayName = self.args['player']['commonName'] if self.args['player']['commonName'] is not '' else self.args['player']['lastName']
        self.text.insert(tk.END, '%s    Set Bid Options for %s...\n' % (time.strftime('%Y-%m-%d %H:%M:%S'), self.displayName))
        self.text.see(tk.END)
        img = ImageTk.PhotoImage(create(self.args['player']))
        self.card.config(image=img)
        self.card.image = img
        self.update_idletasks()
        self.auctionsWon = 0
        self.sold = 0

from frames.login import Login
from frames.playersearch import PlayerSearch
from frames.watch import Watch
from fut.exceptions import FutError, PermissionDenied, ExpiredSession
from requests.exceptions import RequestException
