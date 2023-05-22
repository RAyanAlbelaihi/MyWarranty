import os.path
import threading
import pymysql
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivymd.app import MDApp
from kivymd.icon_definitions import md_icons
from kivymd.toast import toast
from kivymd.uix.behaviors import CommonElevationBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.label import MDLabel
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.list import TwoLineAvatarListItem, IRightBodyTouch, OneLineAvatarListItem, ThreeLineListItem, \
    ThreeLineIconListItem, IconRightWidget, ThreeLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from dateutil.relativedelta import relativedelta
from kivymd.uix.selection import MDSelectionList
from kivymd.uix.sliverappbar import MDSliverAppbar, MDSliverAppbarContent
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.textfield import MDTextField
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivymd.uix.button import MDFloatingActionButtonSpeedDial
from datetime import datetime, date, timedelta
import plyer
from jnius import autoclass
import sys
from threading import Thread
import settings
from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from threading import Thread
from shutil import copyfile
import yagmail

Window.size = (350, 600)

user_id = 0
fname = ''
lname = ''
address = ''
phone = ''
email = ''
password = ''
user_type = ''

offer_price = 0
offer_duration = 0

all_items = []
items_list = []
warranty_list = ()

try:
    conn = pymysql.connect(host='localhost', user='root', password='toor')
    cursor = conn.cursor()
    query = 'CREATE DATABASE IF NOT EXISTS DB'
    cursor.execute(query)
    query = 'use DB'
    cursor.execute(query)
    query = "CREATE TABLE IF NOT EXISTS user (user_id int auto_increment primary key not null, first_name varchar(50) not null, last_name varchar(50) not null, user_address varchar(100) not null, user_phone int, user_email varchar(100) not null, user_password varchar(32) not null, user_type varchar(25) not null)"
    cursor.execute(query)

    query = "CREATE TABLE IF NOT EXISTS invoice (invoice_id int auto_increment primary key not null, user_id int not null, foreign key (user_id) references user(user_id), invoice_date date not null, invoice_total decimal not null, store_name varchar(50) not null, store_address varchar(100) not null)"
    cursor.execute(query)

    query = "CREATE TABLE IF NOT EXISTS items (item_id int auto_increment primary key not null, invoice_id int not null, foreign key (invoice_id) references invoice(invoice_id), item_name varchar(50) not null, item_type varchar(100) not null, item_price decimal not null)"
    cursor.execute(query)

    query = "CREATE TABLE IF NOT EXISTS warranty (warranty_id int auto_increment primary key not null, user_id int not null, foreign key(user_id) references user(user_id), warranty_items varchar(100) not null, warranty_price decimal not null, starting_date date not null, expiring_date date, store_name varchar(50) not null, store_address varchar(100), provider_name varchar(50), serial_number varchar(100) not null, constraint uq_warranty_items unique (warranty_items))"
    cursor.execute(query)

    query = "CREATE TABLE IF NOT EXISTS offers (offer_id int auto_increment primary key not null, user_id int not null, foreign key (user_id) references user(user_id), company_id int not null, warranty_id int, foreign key (warranty_id) references warranty(warranty_id), item_id int, foreign key (item_id) references items(item_id), offer_date date, offer_time time, offer_duration int, offer_price decimal, approved_date date, approved_time time)"
    cursor.execute(query)

    query = "CREATE TABLE IF NOT EXISTS report (report_id int auto_increment primary key not null, user_id int not null, foreign key (user_id) references user(user_id), report_date date not null, report_time time, report_duration int not null, report_region varchar(50) not null, report_file varchar(100))"
    cursor.execute(query)
except:
    pass

kv = """

<Check@MDCheckbox>:
    group: 'group'
    size_hint: None, None
    size: dp(48), dp(48)

<Content>:
    price: price
    duration: duration

    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        id: price
        hint_text: "Price"
        on_text: root.get_offer()

    MDTextField:
        id: duration
        hint_text: "Duration (Months)"
        on_text: root.get_offer()

<Merchant>:
    address: address
    type: type
    item: item
    duration: duration

    orientation: "vertical"
    spacing: "8dp"
    size_hint_y: None
    height: "250dp"

    MDTextField:
        id: address
        hint_text: "Address"
        on_text: root.get_report()
        
    MDTextField:
        id: type
        hint_text: "Type"
        on_text: root.get_report()

    MDTextField:
        id: item
        hint_text: "Item"
        on_text: root.get_report()
        
    MDTextField:
        id: duration
        hint_text: "Duration (Months)"
        on_text: root.get_report()
    
        
<Customer>:
    duration: duration

    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "60dp"

    MDTextField:
        id: duration
        hint_text: "Duration (Months)"
        on_text: root.get_report()
        
ScreenManagement:

    LoginScreen:
    RegisterScreen:
    MainScreen:
    ForgotScreen:

<LoginScreen>:
    name: 'loginscreen'
    Card:
        md_bg_color: 1, 1, 1, 1
        elevation: 5
        size_hint: .85, .9
        pos_hint: {"center_x": .5, "center_y": .5}
        radius: [10]
        Image:
            source: "logo.png"
            size_hint: 1, 1
            pos_hint: {"center_x": .5, "center_y": .78}
        MDFloatLayout:
            size_hint: .85, .08
            pos_hint: {"center_x": .5, "center_y": .52}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
            MDTextField:
                id: email
                icon_right: "account"
                hint_text: "Email / Phone Number"
                size_hint: .9, None
                pos_hint: {"center_x": .5, "center_y": .5}
                height: self.minimum_height
                multiline: False
                cursor_color: 57/255, 66/255, 143/255, 1
                cursor_width: "2sp"
                foreground_color: 57/255, 66/255, 143/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_size: "18sp"

        MDFloatLayout:
            size_hint: .85, .08
            pos_hint: {"center_x": .5, "center_y": .41}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
            MDTextField:
                id: password
                hint_text: "Password"
                size_hint: .9, None
                pos_hint: {"center_x": .5, "center_y": .5}
                height: self.minimum_height
                multiline: False
                password: True
                cursor_color: 57/255, 66/255, 143/255, 1
                cursor_width: "2sp"
                foreground_color: 57/255, 66/255, 143/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_size: "18sp"
            MDIconButton:
                id: show
                halign: 'center'
                icon: 'eye'
                font_size: '30sp'
                pos_hint: {'center_x': .9, 'center_y': .5}
                on_release: app.show_password("login")
        Button:
            text: "Login"
            font_size: "18sp"
            size_hint: .4, .08
            pos_hint: {"center_x": .5, "center_y": .2}
            background_color: 0, 0, 0, 0
            color: 1, 1, 1, 1
            on_release: app.login_process()
            canvas.before:
                Color:
                    rgb: 11/255, 205/255, 215/255
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
        Button:
            text: "Register"
            font_size: "18sp"
            size_hint: .4, .08
            pos_hint: {"center_x": .5, "center_y": .1}
            background_color: 0, 0, 0, 0
            color: 1, 1, 1, 1
            on_release: app.root.current = "registerscreen"
            canvas.before:
                Color:
                    rgb: 215/255, 154/255, 11/255
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
        MDTextButton:
            text: "Forgot Password?"
            pos_hint: {"center_x": .5, "center_y": .3}
            font_size: "16sp"
            halign: "center"
            on_press: app.root.current = "forgotscreen"
<RegisterScreen>:
    name: 'registerscreen'
    Card:
        md_bg_color: 1, 1, 1, 1
        elevation: 5
        size_hint: .85, .9
        pos_hint: {"center_x": .5, "center_y": .5}
        radius: [10]
        MDFloatLayout:
            size_hint: .85, .08
            pos_hint: {"center_x": .5, "center_y": .8}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
            MDTextField:
                id: email
                icon_right: "email"
                hint_text: "Email"
                size_hint: .9, None
                pos_hint: {"center_x": .5, "center_y": .5}
                height: self.minimum_height
                multiline: False
                cursor_color: 57/255, 66/255, 143/255, 1
                cursor_width: "2sp"
                foreground_color: 57/255, 66/255, 143/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_size: "18sp"
        MDFloatLayout:
            size_hint: .85, .08
            pos_hint: {"center_x": .5, "center_y": .7}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
            MDTextField:
                id: password
                hint_text: "Password"
                size_hint: .9, None
                pos_hint: {"center_x": .5, "center_y": .5}
                height: self.minimum_height
                multiline: False
                password: True
                cursor_color: 57/255, 66/255, 143/255, 1
                cursor_width: "2sp"
                foreground_color: 57/255, 66/255, 143/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_size: "18sp"
            MDIconButton:
                id: show
                halign: 'center'
                icon: 'eye'
                font_size: '30sp'
                pos_hint: {'center_x': .9, 'center_y': .5}
                on_release: app.show_password("register")
        MDFloatLayout:
            size_hint: .85, .08
            pos_hint: {"center_x": .5, "center_y": .6}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
            MDTextField:
                id: fname
                icon_right: "account"
                hint_text: "First Name"
                size_hint: .9, None
                pos_hint: {"center_x": .5, "center_y": .5}
                height: self.minimum_height
                multiline: False
                cursor_color: 57/255, 66/255, 143/255, 1
                cursor_width: "2sp"
                foreground_color: 57/255, 66/255, 143/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_size: "18sp"
        MDFloatLayout:
            size_hint: .85, .08
            pos_hint: {"center_x": .5, "center_y": .5}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
            MDTextField:
                id: lname
                icon_right: "account"
                hint_text: "Last Name"
                size_hint: .9, None
                pos_hint: {"center_x": .5, "center_y": .5}
                height: self.minimum_height
                multiline: False
                cursor_color: 57/255, 66/255, 143/255, 1
                cursor_width: "2sp"
                foreground_color: 57/255, 66/255, 143/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_size: "18sp"
        MDFloatLayout:
            size_hint: .85, .08
            pos_hint: {"center_x": .5, "center_y": .4}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
            MDTextField:
                id: phone
                icon_right: "phone"
                hint_text: "Phone Number"
                size_hint: .9, None
                pos_hint: {"center_x": .5, "center_y": .5}
                height: self.minimum_height
                multiline: False
                cursor_color: 57/255, 66/255, 143/255, 1
                cursor_width: "2sp"
                foreground_color: 57/255, 66/255, 143/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_size: "18sp"
        MDFloatLayout:
            size_hint: .85, .08
            pos_hint: {"center_x": .5, "center_y": .3}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
            MDTextField:
                id: address
                icon_right: "map"
                hint_text: "Address"
                size_hint: .9, None
                pos_hint: {"center_x": .5, "center_y": .5}
                height: self.minimum_height
                multiline: False
                cursor_color: 57/255, 66/255, 143/255, 1
                cursor_width: "2sp"
                foreground_color: 57/255, 66/255, 143/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_size: "18sp"
        Button:
            text: "Register"
            font_size: "18sp"
            size_hint: .4, .08
            pos_hint: {"center_x": .5, "center_y": 0.05}
            background_color: 0, 0, 0, 0
            color: 1, 1, 1, 1
            on_release: app.register_process()
            canvas.before:
                Color:
                    rgb: 11/255, 205/255, 215/255
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
        MDLabel:
            text: "Customer"
            pos_hint: {"center_x": .13, "center_y": .2}
            font_size: "16sp"
            halign: "center"
        MDLabel:
            text: "Merchant"
            pos_hint: {"center_x": .5, "center_y": .2}
            font_size: "16sp"
            halign: "center"
        MDLabel:
            text: "Third party"
            pos_hint: {"center_x": .85, "center_y": .2}
            font_size: "16sp"
            halign: "center"
        FloatLayout:
            Check:
                id: customer
                pos_hint: {'center_x': .2, 'center_y': .2}
                active: True
            Check:
                id: merchant
                pos_hint: {'center_x': .6, 'center_y': .2}
            Check:
                id: thirdparty
                pos_hint: {'center_x': 1, 'center_y': .2}
            MDIconButton:
                icon: 'arrow-left'
                pos_hint: {"center_x": .15, "center_y": 1}
                on_release: app.root.current = "loginscreen"
            MDIcon:
                id: userIcon
                halign: 'center'
                icon: 'account-circle'
                font_size: '70sp'
                pos_hint: {'center_x': .6, 'center_y': .97}
<MainScreen>:
    name: 'mainscreen'
    Card:
        id: main
        md_bg_color: 1, 1, 1, 1
        elevation: 5
        size_hint: .85, .9
        pos_hint: {"center_x": .5, "center_y": .5}
        radius: [10]

        MDBottomNavigation:
            pos_hint: {'center_x': .5, 'center_y': .5}
            MDBottomNavigationItem:
                name: 'home'
                id: home
                icon: 'home'
                on_tab_press: app.refresh_screen()
                MDTabs:
                    id: tabs
                    Tab:
                        title: "Active"
                        MDScrollView:
                            MDList:
                                id: active
                    Tab:
                        title: "Expiring Soon"
                        MDScrollView:
                            MDList:
                                id: expiring_soon
                    Tab:
                        title: "Expired"
                        MDScrollView:
                            MDList:
                                id: expired
                    Tab:
                        title: "Invoices"
                        MDScrollView:
                            MDList:
                                id: invoices
                    Tab:
                        title: "Reports"
                        MDScrollView:
                            MDList:
                                id: report
                    Tab:
                        title: "Orders"
                        MDScrollView:
                            MDList:
                                id: orders
                                
            MDBottomNavigationItem:
                name: 'reports'
                id: reports
                icon: 'file-document'
                on_tab_press: app.prepare_report()
                        
            MDBottomNavigationItem:
                name: 'add'
                id: plus
                icon: 'plus'
                on_tab_press: app.dropdown()

            MDBottomNavigationItem:
                name: 'extended'
                id: extended
                icon: 'autorenew'
                on_tab_press: app.refresh_screen()
                on_tab_press: app.warranty_extended()

            MDBottomNavigationItem:
                name: 'account'
                icon: 'account'
                on_tab_press: app.refresh_screen()
                on_tab_press: app.get_user_info()

                MDLabel:
                    text: "Account"
                    pos_hint: {"center_x": .15, "center_y": .9}
                    font_size: "16sp"
                    color: "gray"
                    halign: "center" 
                MDFloatLayout:
                    size_hint: .85, .08
                    pos_hint: {"center_x": .5, "center_y": .8}
                    canvas:
                        Color:
                            rgb: (238/255, 238/255, 238/255, 1)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [22]
                    TextInput:
                        id: email
                        hint_text: "Email"
                        size_hint: 1, None
                        pos_hint: {"center_x": .5, "center_y": .5}
                        height: self.minimum_height
                        multiline: False
                        cursor_color: 57/255, 66/255, 143/255, 1
                        cursor_width: "2sp"
                        foreground_color: 57/255, 66/255, 143/255, 1
                        background_color: 0, 0, 0, 0
                        padding: 15
                        font_size: "18sp"
                MDFloatLayout:
                    size_hint: .85, .08
                    pos_hint: {"center_x": .5, "center_y": .7}
                    canvas:
                        Color:
                            rgb: (238/255, 238/255, 238/255, 1)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [22]
                    TextInput:
                        id: password
                        hint_text: "Password"
                        size_hint: 1, None
                        pos_hint: {"center_x": .5, "center_y": .5}
                        height: self.minimum_height
                        multiline: False
                        password: True
                        cursor_color: 57/255, 66/255, 143/255, 1
                        cursor_width: "2sp"
                        foreground_color: 57/255, 66/255, 143/255, 1
                        background_color: 0, 0, 0, 0
                        padding: 15
                        font_size: "18sp"
                    MDIconButton:
                        id: show
                        halign: 'center'
                        icon: 'eye'
                        font_size: '30sp'
                        pos_hint: {'center_x': .9, 'center_y': .5}
                        on_release: app.show_password("account")
                MDFloatLayout:
                    size_hint: .85, .08
                    pos_hint: {"center_x": .5, "center_y": .6}
                    canvas:
                        Color:
                            rgb: (238/255, 238/255, 238/255, 1)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [22]
                    TextInput:
                        id: fname
                        hint_text: "First Name"
                        size_hint: 1, None
                        pos_hint: {"center_x": .5, "center_y": .5}
                        height: self.minimum_height
                        multiline: False
                        cursor_color: 57/255, 66/255, 143/255, 1
                        cursor_width: "2sp"
                        foreground_color: 57/255, 66/255, 143/255, 1
                        background_color: 0, 0, 0, 0
                        padding: 15
                        font_size: "18sp"
                MDFloatLayout:
                    size_hint: .85, .08
                    pos_hint: {"center_x": .5, "center_y": .5}
                    canvas:
                        Color:
                            rgb: (238/255, 238/255, 238/255, 1)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [22]
                    TextInput:
                        id: lname
                        hint_text: "Last Name"
                        size_hint: 1, None
                        pos_hint: {"center_x": .5, "center_y": .5}
                        height: self.minimum_height
                        multiline: False
                        cursor_color: 57/255, 66/255, 143/255, 1
                        cursor_width: "2sp"
                        foreground_color: 57/255, 66/255, 143/255, 1
                        background_color: 0, 0, 0, 0
                        padding: 15
                        font_size: "18sp"
                MDFloatLayout:
                    size_hint: .85, .08
                    pos_hint: {"center_x": .5, "center_y": .4}
                    canvas:
                        Color:
                            rgb: (238/255, 238/255, 238/255, 1)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [22]
                    TextInput:
                        id: phone
                        hint_text: "Phone Number"
                        size_hint: 1, None
                        pos_hint: {"center_x": .5, "center_y": .5}
                        height: self.minimum_height
                        multiline: False
                        cursor_color: 57/255, 66/255, 143/255, 1
                        cursor_width: "2sp"
                        foreground_color: 57/255, 66/255, 143/255, 1
                        background_color: 0, 0, 0, 0
                        padding: 15
                        font_size: "18sp"
                MDFloatLayout:
                    size_hint: .85, .08
                    pos_hint: {"center_x": .5, "center_y": .3}
                    canvas:
                        Color:
                            rgb: (238/255, 238/255, 238/255, 1)
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [22]
                    TextInput:
                        id: address
                        hint_text: "Address"
                        size_hint: 1, None
                        pos_hint: {"center_x": .5, "center_y": .5}
                        height: self.minimum_height
                        multiline: False
                        cursor_color: 57/255, 66/255, 143/255, 1
                        cursor_width: "2sp"
                        foreground_color: 57/255, 66/255, 143/255, 1
                        background_color: 0, 0, 0, 0
                        padding: 15
                        font_size: "18sp"
                MDLabel:
                    text: "Dark Mode"
                    color: "gray"
                    pos_hint: {"center_x": .6, "center_y": .2}

                MDSwitch:
                    pos_hint: {"center_x": .8, "center_y": .2}
                    thumb_color_active: "white"
                    thumb_color_inactive: "black"
                    on_active: app.dark(*args)
                Button:
                    text: "Update"
                    font_size: "18sp"
                    size_hint: .4, .08
                    pos_hint: {"center_x": .25, "center_y": 0.1}
                    background_color: 0, 0, 0, 0
                    color: 1, 1, 1, 1
                    on_press: app.update_user()
                    canvas.before:
                        Color:
                            rgb: 11/255, 205/255, 215/255
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [22]
                Button:
                    text: "Logout"
                    font_size: "18sp"
                    size_hint: .4, .08
                    pos_hint: {"center_x": .75, "center_y": 0.1}
                    background_color: 0, 0, 0, 0
                    color: 1, 1, 1, 1
                    on_press: app.root.current = "loginscreen"
                    canvas.before:
                        Color:
                            rgb: 11/255, 205/255, 215/255
                        RoundedRectangle:
                            size: self.size
                            pos: self.pos
                            radius: [22]
<ForgotScreen>:
    name: 'forgotscreen'
    Card:
        md_bg_color: 1, 1, 1, 1
        elevation: 5
        size_hint: .85, .9
        pos_hint: {"center_x": .5, "center_y": .5}
        radius: [10]
        Image:
            source: "logo.png"
            size_hint: 1, 1
            pos_hint: {"center_x": .5, "center_y": .78}
        MDFloatLayout:
            size_hint: .85, .08
            pos_hint: {"center_x": .5, "center_y": .52}
            canvas:
                Color:
                    rgb: (238/255, 238/255, 238/255, 1)
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]
            TextInput:
                id: email
                hint_text: "Email"
                size_hint: 1, None
                pos_hint: {"center_x": .5, "center_y": .5}
                height: self.minimum_height
                multiline: False
                cursor_color: 57/255, 66/255, 143/255, 1
                cursor_width: "2sp"
                foreground_color: 57/255, 66/255, 143/255, 1
                background_color: 0, 0, 0, 0
                padding: 15
                font_size: "18sp"
        Button:
            text: "Send Password"
            font_size: "18sp"
            size_hint: .5, .08
            pos_hint: {"center_x": .5, "center_y": .4}
            background_color: 0, 0, 0, 0
            color: 1, 1, 1, 1
            on_release: app.forgot_password()
            canvas.before:
                Color:
                    rgb: 11/255, 205/255, 215/255
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [22]

        MDIconButton:
            icon: 'arrow-left'
            pos_hint: {"center_x": .1, "center_y": .95}
            on_release: app.root.current = "loginscreen"
"""


class ScreenManagement(ScreenManager):
    pass


class LoginScreen(Screen):
    pass


class RegisterScreen(Screen):
    pass


class MainScreen(Screen):
    pass


class ForgotScreen(Screen):
    pass


class Card(CommonElevationBehavior, MDFloatLayout):
    pass


class Tab(MDFloatLayout, MDTabsBase):
    pass


class Item(OneLineAvatarListItem):
    divider = None
    selected = StringProperty()


class all(ThreeLineAvatarIconListItem):
    divider = None
    selected = StringProperty()


class Content(BoxLayout):
    price = ObjectProperty(None)
    duration = ObjectProperty(None)

    def get_offer(self):
        global offer_price, offer_duration
        offer_price = self.price.text
        offer_duration = self.duration.text


class Merchant(BoxLayout):
    address = ObjectProperty(None)
    type = ObjectProperty(None)
    item = ObjectProperty(None)
    duration = ObjectProperty(None)

    def get_report(self):
        global report_address, report_item, report_duration, report_type
        report_address = self.address.text
        report_type = self.type.text
        report_item = self.item.text
        report_duration = self.duration.text


class Customer(BoxLayout):
    duration = ObjectProperty(None)

    def get_report(self):
        global report_duration
        report_duration = self.duration.text


class App(MDApp):
    container = ObjectProperty(None)
    data_list = ListProperty([])
    filemanager = None

    def login_process(self):
        global email, password, user_id, fname, lname, address, phone, user_type
        email = self.root.get_screen('loginscreen').ids.email.text
        password = self.root.get_screen('loginscreen').ids.password.text

        if "@" in email:
            try:
                query = "SELECT * FROM user WHERE user_email=%s and user_password= BINARY %s"
                cursor.execute(query, (email, password))
                row = cursor.fetchone()
            except:
                pass
        else:
            try:
                query = "SELECT * FROM user WHERE user_phone=%s and user_password= BINARY %s"
                cursor.execute(query, (email, password))
                row = cursor.fetchone()
            except:
                pass

        try:
            if row == None:
                toast("Invalid Credentials")
            else:
                if "@" in email:
                    query = "SELECT * FROM user WHERE user_email=%s and user_password=%s"
                else:
                    query = "SELECT * FROM user WHERE user_phone=%s and user_password=%s"
                cursor.execute(query, (email, password))
                user_info = cursor.fetchone()
                user_id = user_info[0]
                fname = user_info[1]
                lname = user_info[2]
                address = user_info[3]
                phone = user_info[4]
                user_type = user_info[7]
                toast("Successful Login")
                self.root.current = "mainscreen"
        except:
            toast("Connection Error!")
        self.get_items()
        self.show_notification()

    def register_process(self):
        email = self.root.get_screen('registerscreen').ids.email.text
        password = self.root.get_screen('registerscreen').ids.password.text
        fname = self.root.get_screen('registerscreen').ids.fname.text
        lname = self.root.get_screen('registerscreen').ids.lname.text
        phone = self.root.get_screen('registerscreen').ids.phone.text
        address = self.root.get_screen('registerscreen').ids.address.text

        try:
            query = "SELECT * FROM user WHERE user_email=%s"
            cursor.execute(query, email)
            row = cursor.fetchone()
            if row != None:
                toast("Email is already registered !")
            else:
                query = "SELECT * FROM user WHERE user_phone=%s"
                cursor.execute(query, phone)
                row = cursor.fetchone()
                if row != None:
                    toast("Phone number is already registered !")
                else:
                    if self.root.get_screen('registerscreen').ids.customer.active:
                        type = 'Customer'
                    elif self.root.get_screen('registerscreen').ids.merchant.active:
                        type = 'Merchant'
                    elif self.root.get_screen('registerscreen').ids.thirdparty.active:
                        type = 'Third Party'

                    query = "INSERT INTO user (first_name,last_name,user_address,user_phone,user_email,user_password,user_type) values(%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(query, (fname, lname, address, phone, email, password, type))
                    conn.commit()
                    query = "SELECT user_id FROM user WHERE user_email=%s and user_password=%s"
                    cursor.execute(query, (email, password))
                    user_id = cursor.fetchone()[0]
                    toast("Successful Register")
                    self.root.current = "mainscreen"
        except:
            toast("Connection Error!")

    def show_password(self, screen):
        if screen == "login":
            if self.root.get_screen('loginscreen').ids.show.icon == "eye":
                self.root.get_screen('loginscreen').ids.password.password = False
                self.root.get_screen('loginscreen').ids.show.icon = 'eye-off'
            else:
                self.root.get_screen('loginscreen').ids.password.password = True
                self.root.get_screen('loginscreen').ids.show.icon = 'eye'
        elif screen == "register":
            if self.root.get_screen('registerscreen').ids.show.icon == "eye":
                self.root.get_screen('registerscreen').ids.password.password = False
                self.root.get_screen('registerscreen').ids.show.icon = 'eye-off'
            else:
                self.root.get_screen('registerscreen').ids.password.password = True
                self.root.get_screen('registerscreen').ids.show.icon = 'eye'
        elif screen == "account":
            if self.root.get_screen('mainscreen').ids.show.icon == "eye":
                self.root.get_screen('mainscreen').ids.password.password = False
                self.root.get_screen('mainscreen').ids.show.icon = 'eye-off'
            else:
                self.root.get_screen('mainscreen').ids.password.password = True
                self.root.get_screen('mainscreen').ids.show.icon = 'eye'

    def forgot_password(self):
        email = self.root.get_screen('forgotscreen').ids.email.text
        query = "SELECT * FROM user WHERE user_email = %s"
        cursor.execute(query, email)
        user_information = cursor.fetchone()
        first_name = user_information[1]
        last_name = user_information[2]
        password = user_information[6]
        yag = yagmail.SMTP('MyWarrantyQU@gmail.com', 'bmboesfmfgcwopjc')
        contents = [
            f"<h2>Hello {first_name} {last_name}, </h2>\n\n<h3>It seems like you forgot your password for My Warranty!</h3>\n\n\n <h3>Your password is: {password}</h3>"
        ]
        yag.send(email, 'Password Reset', contents)
        toast("Your password has been sent to your Email")

    def dropdown(self):
        self.menu_list = [
            {
                "viewclass": "OneLineListItem",
                "id": "drop1",
                "text": "Add a warranty",
                "on_release": lambda x="Add a warranty": self.menu1()
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Add an invoice",
                "on_release": lambda x="Add an invoice": self.menu2()
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.root.get_screen('mainscreen').ids.plus,
            items=self.menu_list,
            width_mult=4,
        )
        self.menu.open()

    def menu1(self):
        global doc
        doc = 'Warranty'
        self.menu.dismiss()
        self.add_list = [
            {
                "viewclass": "OneLineListItem",
                "text": "Upload a photo",
                "on_release": lambda x="Upload a photo": self.file()
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Enter manually",
                "on_release": lambda x="Enter manually": self.warranty_manually()
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.root.get_screen('mainscreen').ids.plus,
            items=self.add_list,
            width_mult=4,
        )
        self.menu.open()

    def menu2(self):
        global doc
        doc = 'Invoice'
        self.menu.dismiss()
        self.add_list = [
            {
                "viewclass": "OneLineListItem",
                "text": "Upload a photo",
                "on_release": lambda x="Upload a photo": self.file()
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Enter manually",
                "on_release": lambda x="Enter manually": self.invoice_manually()
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.root.get_screen('mainscreen').ids.plus,
            items=self.add_list,
            width_mult=4,
        )
        self.menu.open()

    def warranty_manually(self):
        self.menu.dismiss()
        starting_date = TextInput(
            hint_text="Starting date (YYYY-MM-DD)",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .75},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp",
        )
        starting_date_icon = MDIconButton(
            icon="calendar",
            icon_size="32sp",
            pos_hint={"center_x": .9, "center_y": .75},
            on_press=lambda *args: self.show_date_picker('starting_date', *args)
        )
        expiring_date = TextInput(
            hint_text="Expiring date (YYYY-MM-DD)",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .65},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp",
        )
        expiring_date_icon = MDIconButton(
            icon="calendar",
            icon_size="32sp",
            pos_hint={"center_x": .9, "center_y": .65},
            on_press=lambda *args: self.show_date_picker('expiring_date', *args)
        )
        store_name = TextInput(
            hint_text="Store name",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .55},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        item_name = TextInput(
            hint_text="Item name",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .95},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        item_price = TextInput(
            hint_text="Item Price",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .85},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        store_address = TextInput(
            hint_text="Store Address",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .45},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        provider_name = TextInput(
            hint_text="Warranty Provider Name",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .35},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        serial_number = TextInput(
            hint_text="Serial Number",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .25},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        add_button = Button(
            text="Add",
            size_hint=(.4, .08),
            pos_hint={"center_x": .5, "center_y": .15},
            font_size="18sp",
            color=(1, 1, 1, 1),
            on_press=self.add_warranty
        )

        self.root.get_screen('mainscreen').ids.main.add_widget(item_name)
        self.root.get_screen('mainscreen').ids.main.ids['item_name'] = item_name
        self.root.get_screen('mainscreen').ids.main.add_widget(item_price)
        self.root.get_screen('mainscreen').ids.main.ids['item_price'] = item_price
        self.root.get_screen('mainscreen').ids.main.add_widget(starting_date)
        self.root.get_screen('mainscreen').ids.main.ids['starting_date'] = starting_date
        self.root.get_screen('mainscreen').ids.main.add_widget(starting_date_icon)
        self.root.get_screen('mainscreen').ids.main.ids['starting_date_icon'] = starting_date_icon
        self.root.get_screen('mainscreen').ids.main.add_widget(expiring_date)
        self.root.get_screen('mainscreen').ids.main.ids['expiring_date'] = expiring_date
        self.root.get_screen('mainscreen').ids.main.add_widget(expiring_date_icon)
        self.root.get_screen('mainscreen').ids.main.ids['expiring_date_icon'] = expiring_date_icon
        self.root.get_screen('mainscreen').ids.main.add_widget(store_name)
        self.root.get_screen('mainscreen').ids.main.ids['store_name'] = store_name
        self.root.get_screen('mainscreen').ids.main.add_widget(store_address)
        self.root.get_screen('mainscreen').ids.main.ids['store_address'] = store_address
        self.root.get_screen('mainscreen').ids.main.add_widget(provider_name)
        self.root.get_screen('mainscreen').ids.main.ids['provider_name'] = provider_name
        self.root.get_screen('mainscreen').ids.main.add_widget(serial_number)
        self.root.get_screen('mainscreen').ids.main.ids['serial_number'] = serial_number
        self.root.get_screen('mainscreen').ids.main.add_widget(add_button)
        self.root.get_screen('mainscreen').ids.main.ids['add_button'] = add_button

    def invoice_manually(self):
        self.menu.dismiss()
        invoice_date = TextInput(
            hint_text="Invoice Date (YYYY-MM-DD)",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .95},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        date_icon = MDIconButton(
            icon="calendar",
            icon_size="32sp",
            pos_hint={"center_x": .9, "center_y": .95},
            on_press=lambda *args: self.show_date_picker('Invoice', *args)
        )
        invoice_total = TextInput(
            hint_text="Invoice Total",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .85},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        store_name = TextInput(
            hint_text="Store Name",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .75},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        store_address = TextInput(
            hint_text="Store Address",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .65},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        item_name = TextInput(
            hint_text="Item Name",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .55},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        item_type = TextInput(
            hint_text="Item Type",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .45},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        item_price = TextInput(
            hint_text="Item Price",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .35},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        add_button = Button(
            text="Add",
            size_hint=(.4, .08),
            pos_hint={"center_x": .5, "center_y": .25},
            font_size="18sp",
            color=(1, 1, 1, 1),
            on_press=self.add_invoice
        )

        self.root.get_screen('mainscreen').ids.main.add_widget(invoice_date)
        self.root.get_screen('mainscreen').ids.main.ids['invoice_date'] = invoice_date
        self.root.get_screen('mainscreen').ids.main.add_widget(date_icon)
        self.root.get_screen('mainscreen').ids.main.ids['date_icon'] = date_icon
        self.root.get_screen('mainscreen').ids.main.add_widget(invoice_total)
        self.root.get_screen('mainscreen').ids.main.ids['invoice_total'] = invoice_total
        self.root.get_screen('mainscreen').ids.main.add_widget(store_name)
        self.root.get_screen('mainscreen').ids.main.ids['store_name'] = store_name
        self.root.get_screen('mainscreen').ids.main.add_widget(store_address)
        self.root.get_screen('mainscreen').ids.main.ids['store_address'] = store_address
        self.root.get_screen('mainscreen').ids.main.add_widget(item_name)
        self.root.get_screen('mainscreen').ids.main.ids['item_name'] = item_name
        self.root.get_screen('mainscreen').ids.main.add_widget(item_type)
        self.root.get_screen('mainscreen').ids.main.ids['item_type'] = item_type
        self.root.get_screen('mainscreen').ids.main.add_widget(item_price)
        self.root.get_screen('mainscreen').ids.main.ids['item_price'] = item_price

        self.root.get_screen('mainscreen').ids.main.add_widget(add_button)
        self.root.get_screen('mainscreen').ids.main.ids['add_button'] = add_button

    def get_user_info(self):
        global email, password, user_id, fname, lname, address, phone

        query = "SELECT * FROM user WHERE user_id = %s"
        cursor.execute(query, user_id)
        user = cursor.fetchone()

        self.root.get_screen('mainscreen').ids.fname.text = user[1]
        self.root.get_screen('mainscreen').ids.lname.text = user[2]
        self.root.get_screen('mainscreen').ids.address.text = user[3]
        self.root.get_screen('mainscreen').ids.phone.text = f"{user[4]}"
        self.root.get_screen('mainscreen').ids.email.text = user[5]
        self.root.get_screen('mainscreen').ids.password.text = user[6]

    def update_user(self):
        email = self.root.get_screen('mainscreen').ids.email.text
        password = self.root.get_screen('mainscreen').ids.password.text
        fname = self.root.get_screen('mainscreen').ids.fname.text
        lname = self.root.get_screen('mainscreen').ids.lname.text
        phone = self.root.get_screen('mainscreen').ids.phone.text
        address = self.root.get_screen('mainscreen').ids.address.text

        query = "UPDATE user SET first_name = %s,last_name = %s,user_address = %s,user_phone = %s,user_email = %s,user_password = %s WHERE user_id = %s"
        cursor.execute(query, (fname, lname, address, phone, email, password, user_id))
        conn.commit()
        toast("Information Updated")

    def dark(self, checkbox, value):
        if value:
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

    def warranty_extended(self):
        global all_items, items_list, warranty_list, user_type

        invoices_list = []
        if user_type == "Third Party":
            self.extended_list = [
                {
                    "viewclass": "OneLineListItem",
                    "text": "Offers Requests",
                    "on_release": lambda x="Offers Requests": self.new_offers()
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "Approved Offers",
                    "on_release": lambda x="Approved Offers": self.approved_offers()
                }
            ]
            self.menu = MDDropdownMenu(
                caller=self.root.get_screen('mainscreen').ids.extended,
                items=self.extended_list,
                width_mult=4,
            )
        else:
            self.extended_list = [
                {
                    "viewclass": "OneLineListItem",
                    "text": "New Offer",
                    "on_release": lambda x="New Offer": self.offer_select_item()
                },
                {
                    "viewclass": "OneLineListItem",
                    "text": "View Offers",
                    "on_release": lambda x="View Offers": self.view_offer()
                }
            ]
        self.menu = MDDropdownMenu(
            caller=self.root.get_screen('mainscreen').ids.extended,
            items=self.extended_list,
            width_mult=4,
        )

        self.menu.open()

        query = "SELECT invoice_id FROM invoice WHERE user_id = %s"
        cursor.execute(query, user_id)
        invoices = cursor.fetchall()

        for i in range(len(invoices)):
            invoices_list.append(invoices[i][0])

        query = "SELECT * from items WHERE invoice_id = %s"
        for i in invoices_list:
            cursor.execute(query, i)
            items_list.append(cursor.fetchall())

        query = "SELECT * FROM warranty WHERE user_id = %s"
        cursor.execute(query, user_id)
        warranty_list = cursor.fetchall()

        if (items_list != [] or warranty_list != ()) and all_items == []:
            for i in range(len(items_list[0])):
                all_items.append(items_list[0][i][2])
            if warranty_list != ():
                for i in range(len(warranty_list)):
                    all_items.append(warranty_list[i][2])

    def offer_select_item(self):
        global all_items
        self.menu.dismiss()

        items_menu = [{"text": f"{all_items[i]}", "viewclass": "OneLineListItem"} for i in range(len(all_items))]

        self.dialog = MDDialog(
            title="Select the item",
            type="simple",
            items=[Item(text=f"{all_items[i]}", selected=f"{all_items[i]}", on_press=self.offer_request) for i in
                   range(len(all_items))],
        )
        self.dialog.open()

    def offer_request(self, obj):
        global items_list, warranty_list
        Found = False

        # Create table for New User Warranty extended Requests
        query = "CREATE TABLE IF NOT EXISTS requests (request_id int auto_increment primary key not null, item_id int, foreign key (item_id) references items(item_id), warranty_id int, foreign key (warranty_id) references warranty(warranty_id))"
        cursor.execute(query)

        if Found == False:
            for i in range(len(items_list)):
                if items_list[i] == ():
                    pass
                elif items_list[i][0][2] == obj.selected:
                    Found = True
                    item_id = items_list[i][0][0]
                    query = "INSERT INTO requests (item_id) values(%s)"
                    cursor.execute(query, item_id)
                    conn.commit()
        if Found == False:
            for i in range(len(warranty_list)):
                if warranty_list[i][2] == obj.selected:
                    Found = True
                    warranty_id = warranty_list[i][0]
                    query = "INSERT INTO requests (warranty_id) values(%s)"
                    cursor.execute(query, warranty_id)
                    conn.commit()
        toast('Offer Request Sent')
        self.dialog.dismiss()

    def new_offers(self):
        global offers
        self.menu.dismiss()
        items = []
        warrintes = []
        offers = []
        query = "SELECT * FROM requests"
        cursor.execute(query)
        row = cursor.fetchall()

        for i in row:
            if i[1] == None:
                warrintes.append(i[2])
            else:
                items.append(i[1])
        for i in items:
            query = "SELECT item_name, item_price FROM items WHERE item_id = %s"
            cursor.execute(query, i)
            row = cursor.fetchone()
            offers.append(row)

        for i in warrintes:
            query = "SELECT warranty_items, warranty_price FROM warranty WHERE warranty_id = %s"
            cursor.execute(query, i)
            row = cursor.fetchone()
            offers.append(row)

        self.dialog = MDDialog(
            title="New Offers requests",
            type="simple",
            items=[Item(text=f"{i[0]} [{i[1]}]", selected=f"{i[0]}", on_press=self.create_offer) for i in offers],
        )
        self.dialog.open()

    def view_offer(self):
        global user_id
        invoices = []
        items = []
        requests = []
        duration = []
        price = []
        requests_ids = []
        company_id = []
        company_name = []
        offers = []
        warrintes = []
        pending = ()

        query = "SELECT invoice_id FROM invoice WHERE user_id = %s"
        cursor.execute(query, user_id)
        invoice_no = cursor.fetchall()

        query = "SELECT warranty_id FROM warranty WHERE user_id = %s"
        cursor.execute(query, user_id)
        warranty_no = cursor.fetchall()

        if invoice_no != None:
            for i in invoice_no:
                invoices.append(i[0])
            for i in invoices:
                query = "SELECT item_id FROM items WHERE invoice_id = %s"
                cursor.execute(query, i)
                items_ids = cursor.fetchall()
                if items_ids != None:
                    if items_ids != ():
                        items.append(items_ids[0][0])

        if warranty_no != None:
            for i in warranty_no:
                warrintes.append(i[0])

        if items != []:
            for i in items:
                query = "SELECT request_id FROM requests WHERE item_id = %s"
                cursor.execute(query, i)
                request_id = cursor.fetchall()
                for j in request_id:
                    if j != ():
                        requests.append(request_id[0][0])
        if warrintes != []:
            for i in warrintes:
                query = "SELECT request_id FROM requests WHERE warranty_id = %s"
                cursor.execute(query, i)
                request_id = cursor.fetchall()
                for j in request_id:
                    if j != ():
                        requests.append(request_id[0][0])

        if requests != []:
            for i in requests:
                query = "SELECT * FROM pending WHERE request_id = %s"
                cursor.execute(query, i)
                pending = cursor.fetchall()

        if pending != ():
            for i in pending:
                requests_ids.append(f"#{i[1]}")
                company_id.append(i[2])
                price.append(int(i[5]))
                duration.append(f"{i[6]} Months")

        for i in company_id:
            query = "SELECT first_name, last_name FROM user WHERE user_id = %s"
            cursor.execute(query, i)
            name = cursor.fetchone()
            company_name.append(name[0] + " " + name[1])

        for i in range(len(price)):
            offers.append(f"[{''.join(c for c in requests_ids[i] if c in '0123456789#')}] {''.join(c for c in company_name[i] if c in 'ABCDEFGHJIKLMNOPQRSTUVWXYZ')} ({price[i]}) [{duration[i]}]")

        self.dialog = MDDialog(
            title="Choose an Offer",
            type="simple",
            items=[Item(text=f"{i}", selected=f"{i[2:i.find(']')]}", on_press=self.approve_offer) for i in offers],
        )
        self.dialog.open()

    def create_offer(self, obj):
        global item_selected
        self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Offer:",
            type="custom",
            content_cls=Content(),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_press=self.cancel_button,
                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_press=self.ok_button,
                ),
            ],
        )
        self.dialog.open()
        item_selected = obj.selected

    def ok_button(self, obj):
        global offer_price, offer_duration, item_selected
        selected_id = None

        self.dialog.dismiss()

        offer_date = date.today()
        offer_time = datetime.now().strftime("%H:%M:%S")

        query = "CREATE TABLE IF NOT EXISTS pending (pending_id int auto_increment primary key not null, request_id int, company_id int not null, offer_date date not null, offer_time time, offer_price decimal not null, offer_duration int not null)"
        cursor.execute(query)

        query = "SELECT item_id FROM items WHERE item_name = %s"
        cursor.execute(query, item_selected)
        selected = cursor.fetchone()
        if selected != None:
            selected_id = selected[0]
            query = "SELECT request_id FROM requests WHERE item_id = %s"
            cursor.execute(query, selected_id)
            request_id = cursor.fetchone()[0]

        if selected_id == None:
            query = "SELECT warranty_id from warranty WHERE warranty_items = %s"
            cursor.execute(query, item_selected)
            warranty_id = cursor.fetchone()[0]

            query = "SELECT request_id FROM requests WHERE warranty_id = %s"
            cursor.execute(query, warranty_id)
            request_id = cursor.fetchone()[0]

        query = "INSERT INTO pending (request_id, company_id, offer_date, offer_time, offer_price, offer_duration) values(%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, (request_id, user_id, offer_date, offer_time, offer_price, offer_duration))
        conn.commit()

        toast("Offer sent")

    def cancel_button(self, obj):
        self.dialog.dismiss()
        self.show_notification()

    def show_date_picker(self, type, *args):
        global date_type
        date_type = type
        date_dialog = MDDatePicker(
            year=2022,
            month=1,
            day=1,
        )
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def approve_offer(self, obj):
        approved_date = date.today()
        approved_time = datetime.now().strftime("%H:%M:%S")
        request_id = obj.selected

        query = "SELECT item_id FROM requests WHERE request_id = %s"
        cursor.execute(query, request_id)
        item_id = cursor.fetchone()[0]

        if item_id == None:
            query = "SELECT warranty_id FROM requests WHERE request_id = %s"
            cursor.execute(query, request_id)
            warranty_id = cursor.fetchone()[0]

        query = "SELECT * FROM pending WHERE request_id = %s"
        cursor.execute(query, request_id)
        row = cursor.fetchone()
        company_id = row[2]
        offer_date = row[3]
        offer_time = row[4]
        offer_price = row[5]
        offer_duration = row[6]
        expiring_date = date.today() + relativedelta(months=offer_duration)

        query = "DELETE FROM requests WHERE request_id = %s"
        cursor.execute(query, request_id)
        conn.commit()

        query = "DELETE FROM pending WHERE request_id = %s"
        cursor.execute(query, request_id)
        conn.commit()

        if item_id != None:
            query = "INSERT INTO offers (user_id, company_id, item_id, offer_date, offer_time, offer_duration, offer_price, approved_date, approved_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(query, (
            user_id, company_id, item_id, offer_date, offer_time, offer_duration, offer_price, approved_date,
            approved_time))
            conn.commit()
        else:
            query = "INSERT INTO offers (user_id, company_id, warranty_id, offer_date, offer_time, offer_duration, offer_price, approved_date, approved_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(query, (
            user_id, company_id, warranty_id, offer_date, offer_time, offer_duration, offer_price, approved_date,
            approved_time))
            conn.commit()

            query = "UPDATE warranty SET expiring_date = %s WHERE warranty_id = %s"
            cursor.execute(query, (expiring_date, warranty_id))
            conn.commit()

        self.dialog.dismiss()
        self.get_items()
        toast("Warranty has been extended")

    def approved_offers(self):
        offers = []
        query = "SELECT offer_id FROM offers WHERE company_id = %s"
        cursor.execute(query, user_id)
        offers_no = cursor.fetchall()

        for i in offers_no:
            offers.append(i[0])

        self.dialog = MDDialog(
            title="Approved Offers:",
            type="simple",
            items=[Item(text=f"#{i}", selected=f"{i}", on_press=self.close) for i in offers],
        )
        self.dialog.open()

    def close(self, obj):
        self.dialog.dismiss()

    def on_save(self, instance, value, date_range):
        global date_type
        '''
        :type instance: <kivymd.uix.picker.MDDatePicker object>;
        :param value: selected date;
        :type value: <class 'datetime.date'>;
        :param date_range: list of 'datetime.date' objects in the selected range;
        :type date_range: <class 'list'>;
        '''
        if date_type == "Invoice":
            self.root.get_screen('mainscreen').ids.main.ids.invoice_date.text = value.strftime("%Y-%m-%d")
        elif date_type == "starting_date":
            self.root.get_screen('mainscreen').ids.main.ids.starting_date.text = value.strftime("%Y-%m-%d")
        else:
            self.root.get_screen('mainscreen').ids.main.ids.expiring_date.text = value.strftime("%Y-%m-%d")

    def show_notification(self):
        dates = []
        is_android: bool = hasattr(sys, 'getandroidapilevel')
        if is_android:
            service = autoclass("org.app.mywarranty.ServiceMyWarranty")
            mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
            service.start(mActivity, "")

        query = "SELECT expiring_date FROM warranty WHERE user_id = %s"
        cursor.execute(query, user_id)
        date_inquery = cursor.fetchall()
        for i in date_inquery:
            dates.append(i[0])

        current_time = datetime.now().strftime("%H")
        if current_time == "00":
            for i in dates:
                delta = i - date.today()
                if 0 <= delta.days <= 30:
                    query = "SELECT warranty_items FROM warranty WHERE expiring_date = %s AND user_id = %s"
                    cursor.execute(query, (i, user_id))
                    item_name = cursor.fetchone()[0]
                    plyer.notification.notify(title="Warranty Expiring soon",
                                              message=f"Your warranty for {item_name} will expire in {delta.days} Days")
        if is_android:
            return service

    def file(self):
        self.path = os.path.expanduser("~") or os.path.expanduser("/")
        self.filemanager = MDFileManager(
            select_path=self.select_path,
            exit_manager=self.close_filemanager,
        )
        self.filemanager.show(self.path)

    def select_path(self, path: str):
        global doc
        settings.img_path = path
        self.close_filemanager()
        if doc == 'Warranty':
            self.warranty_manually()
        else:
            self.invoice_manually()
        spinner = MDSpinner(
            size_hint=(None, None),
            pos_hint={"center_x": .5, "center_y": .5},
            active=True,
        )
        self.root.get_screen('mainscreen').ids.main.add_widget(spinner)
        self.root.get_screen('mainscreen').ids.main.ids['spinner'] = spinner
        loading = Thread(target=self.image_processing)
        loading.start()

    def close_filemanager(self, *args):
        self.filemanager.close()

    def image_processing(self, *args):
        import ocr
        self.update_info()

    @mainthread
    def update_info(self):
        self.root.get_screen('mainscreen').ids.main.ids['spinner'].active = False
        try:
            self.root.get_screen('mainscreen').ids.main.ids['item_name'].text = settings.item_list[0]
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.ids['item_price'].text = settings.item_price[0]
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.ids['starting_date'].text = settings.receipt_ocr['Date']
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.ids['store_name'].text = settings.receipt_ocr['CompanyName']
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.ids['store_address'].text = settings.receipt_ocr['Address']
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.ids['provider_name'].text = settings.receipt_ocr['ProviderName']
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.ids['serial_number'].text = settings.receipt_ocr['SerialNumber']
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.ids['invoice_date'].text = settings.receipt_ocr['Date']
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.ids['invoice_total'].text = settings.receipt_ocr['Amount']
        except:
            pass

    def add_invoice(self, obj):
        invoice_date = self.root.get_screen('mainscreen').ids.main.ids['invoice_date'].text
        invoice_total = self.root.get_screen('mainscreen').ids.main.ids['invoice_total'].text
        store_name = self.root.get_screen('mainscreen').ids.main.ids['store_name'].text
        store_address = self.root.get_screen('mainscreen').ids.main.ids['store_address'].text
        item_name = self.root.get_screen('mainscreen').ids.main.ids['item_name'].text
        item_type = self.root.get_screen('mainscreen').ids.main.ids['item_type'].text
        item_price = self.root.get_screen('mainscreen').ids.main.ids['item_price'].text

        query = "INSERT INTO invoice (user_id, invoice_date, invoice_total, store_name, store_address) values(%s,%s,%s,%s,%s)"
        cursor.execute(query, (user_id, invoice_date, invoice_total, store_name, store_address))
        conn.commit()

        query = "SELECT invoice_id FROM invoice WHERE user_id = %s AND invoice_date = %s AND invoice_total = %s AND store_name = %s AND store_address = %s"
        cursor.execute(query, (user_id, invoice_date, invoice_total, store_name, store_address))
        invoice_id = cursor.fetchone()[0]

        query = "INSERT INTO items (invoice_id, item_name, item_type, item_price) values(%s,%s,%s,%s)"
        cursor.execute(query, (invoice_id, item_name, item_type, item_price))
        conn.commit()

        toast('Invoice added')
        self.get_items()
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['invoice_date'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['date_icon'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['invoice_total'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_name'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_address'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_name'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_type'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_price'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['add_button'])

        self.get_items()

    def add_warranty(self, obj):
        item_name = self.root.get_screen('mainscreen').ids.main.ids['item_name'].text
        item_price = self.root.get_screen('mainscreen').ids.main.ids['item_price'].text
        starting_date = self.root.get_screen('mainscreen').ids.main.ids['starting_date'].text
        expiring_date = self.root.get_screen('mainscreen').ids.main.ids['expiring_date'].text
        store_name = self.root.get_screen('mainscreen').ids.main.ids['store_name'].text
        store_address = self.root.get_screen('mainscreen').ids.main.ids['store_address'].text
        provider_name = self.root.get_screen('mainscreen').ids.main.ids['provider_name'].text
        serial_number = self.root.get_screen('mainscreen').ids.main.ids['serial_number'].text

        query = "INSERT INTO warranty (user_id, warranty_items, warranty_price, starting_date, expiring_date, store_name, store_address, provider_name, serial_number) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, (user_id, item_name, item_price, starting_date, expiring_date, store_name, store_address, provider_name,serial_number))
        conn.commit()

        toast('Warranty added')
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_name'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_price'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['starting_date'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['starting_date_icon'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_address'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['expiring_date'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['expiring_date_icon'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_name'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_address'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['provider_name'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['serial_number'])
        self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['add_button'])

        self.get_items()

    def get_items(self):
        active_list = []
        expiring_soon_list = []
        expired_list = []
        y_active = 0.9
        y_expiring = 0.9
        y_expired = 0.9
        y_invoices = 0.9
        y_reports = 0.9
        y_orders = 0.9

        for i in self.root.get_screen('mainscreen').ids.invoices.ids:
            try:
                self.root.get_screen('mainscreen').ids.invoices.remove_widget(self.root.get_screen('mainscreen').ids.invoices.ids[i])
            except:
                pass

        for i in self.root.get_screen('mainscreen').ids.active.ids:
            try:
                self.root.get_screen('mainscreen').ids.active.remove_widget(self.root.get_screen('mainscreen').ids.active.ids[i])
            except:
                pass

        for i in self.root.get_screen('mainscreen').ids.expiring_soon.ids:
            try:
                self.root.get_screen('mainscreen').ids.expiring_soon.remove_widget(self.root.get_screen('mainscreen').ids.expiring_soon.ids[i])
            except:
                pass

        for i in self.root.get_screen('mainscreen').ids.expired.ids:
            try:
                self.root.get_screen('mainscreen').ids.expired.remove_widget(self.root.get_screen('mainscreen').ids.expired.ids[i])
            except:
                pass

        for i in self.root.get_screen('mainscreen').ids.report.ids:
            try:
                self.root.get_screen('mainscreen').ids.report.remove_widget(self.root.get_screen('mainscreen').ids.report.ids[i])
            except:
                pass

        for i in self.root.get_screen('mainscreen').ids.orders.ids:
            try:
                self.root.get_screen('mainscreen').ids.orders.remove_widget(self.root.get_screen('mainscreen').ids.orders.ids[i])
            except:
                pass

        query = "SELECT * FROM invoice WHERE user_id = %s"
        cursor.execute(query, user_id)
        invoices = cursor.fetchall()

        query = "SELECT * FROM warranty WHERE user_id = %s"
        cursor.execute(query, user_id)
        warranty_list = cursor.fetchall()

        query = "SELECT * FROM report WHERE user_id = %s"
        cursor.execute(query, user_id)
        report_list = cursor.fetchall()

        query = "SELECT * FROM offers WHERE user_id = %s"
        cursor.execute(query, user_id)
        order_list = cursor.fetchall()

        for i in warranty_list:
            delta = i[5] - date.today()
            if 0 > delta.days:
                expired_list.append(i)
            elif 0 <= delta.days <= 30:
                expiring_soon_list.append(i)
            else:
                active_list.append(i)

        for i in invoices:
            invoice = all(
                text=f"#{str(i[0])}",
                secondary_text=f"Purchase Date: {str(i[2])}",
                tertiary_text=f"Total: {str(i[3])}",
                pos_hint={"center_x": .5, "center_y": y_invoices},
                selected=f"{i[0]}",
                secondary_text_color="blue",
                tertiary_text_color= (1, 1, 0),
                on_press=lambda *args: self.edit_invoice(*args),
            )
            y_invoices -= 0.17
            self.root.get_screen('mainscreen').ids.invoices.add_widget(invoice)
            self.root.get_screen('mainscreen').ids.invoices.ids[str(i[0])] = invoice
        for i in active_list:
            warranty = all(
                text=str(i[2]),
                secondary_text=f"Price: {str(i[3])}",
                tertiary_text=f"Expiring Date: {str(i[5])}",
                pos_hint={"center_x": .5, "center_y": y_active},
                selected=f"{i[2]}",
                on_press=lambda *args: self.edit_warranty(*args),
            )
            y_active -= 0.17
            self.root.get_screen('mainscreen').ids.active.add_widget(warranty)
            self.root.get_screen('mainscreen').ids.active.ids[i[2]] = warranty

        for i in expiring_soon_list:
            warranty = all(
                text=str(i[2]),
                secondary_text=f"Price: {str(i[3])}",
                tertiary_text=f"Expiring Date: {str(i[5])}",
                pos_hint={"center_x": .5, "center_y": y_expiring},
                selected=f"{i[2]}",
                on_press=lambda *args: self.edit_warranty(*args),
            )
            y_expiring -= 0.17
            self.root.get_screen('mainscreen').ids.expiring_soon.add_widget(warranty)
            self.root.get_screen('mainscreen').ids.expiring_soon.ids[i[2]] = warranty

        for i in expired_list:
            warranty = all(
                text=str(i[2]),
                secondary_text=f"Price: {str(i[3])}",
                tertiary_text=f"Expired on: {str(i[5])}",
                pos_hint={"center_x": .5, "center_y": y_expired},
                selected=f"{i[2]}",
                on_press=lambda *args: self.edit_warranty(*args),
            )
            y_expired -= 0.17
            self.root.get_screen('mainscreen').ids.expired.add_widget(warranty)
            self.root.get_screen('mainscreen').ids.expired.ids[i[2]] = warranty

        for i in report_list:
            report = all(
                text=f"#{str(i[0])}",
                secondary_text=f"Date: {i[2]}",
                tertiary_text=f"Duration: {i[4]}",
                pos_hint={"center_x": .5, "center_y": y_reports},
                selected=f"{i[0]}",
                on_press=lambda *args: self.report_tab(*args),
            )
            y_reports -= 0.17
            self.root.get_screen('mainscreen').ids.report.add_widget(report)
            self.root.get_screen('mainscreen').ids.report.ids[i[0]] = report

        for i in order_list:
            order = all(
                text=f"#{str(i[0])}",
                secondary_text=f"Date: {i[5]}",
                tertiary_text=f"Duration: {i[7]}",
                pos_hint={"center_x": .5, "center_y": y_orders},
                selected=f"{i[0]}",
            )
            y_orders -= 0.17
            self.root.get_screen('mainscreen').ids.orders.add_widget(order)
            self.root.get_screen('mainscreen').ids.orders.ids[i[0]] = order

    @mainthread
    def refresh_screen(self):
        global err
        try:
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_name'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_price'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['starting_date'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['starting_date_icon'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_address'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['expiring_date'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['expiring_date_icon'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_name'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_address'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['provider_name'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['serial_number'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['add_button'])
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['invoice_date'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['date_icon'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['invoice_total'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_name'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['store_address'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_name'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_type'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['item_price'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['add_button'])
        except:
            pass
        try:
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['update_button'])
            self.root.get_screen('mainscreen').ids.main.remove_widget(self.root.get_screen('mainscreen').ids.main.ids['del_button'])
        except:
            pass
        try:
            if err:
                toast("Error! try again later")
                err = False
            elif self.root.get_screen('mainscreen').ids.main.ids['spinner'].active:
                toast("Your report is ready")
                self.get_items()
            self.root.get_screen('mainscreen').ids.main.ids['spinner'].active = False
        except:
            pass

    def loading_report(self, obj):
        global report_duration, report_address, report_item, report_type, user_id

        if user_type == "Merchant":
            settings.report_address = report_address
            settings.report_type = report_type
            settings.report_item = report_item

        settings.user_id = user_id
        settings.report_duration = report_duration
        self.dialog.dismiss()

        spinner = MDSpinner(
            size_hint=(None, None),
            pos_hint={"center_x": .5, "center_y": .5},
            active=True,
        )
        self.root.get_screen('mainscreen').ids.main.add_widget(spinner)
        self.root.get_screen('mainscreen').ids.main.ids['spinner'] = spinner
        loading = Thread(target=self.create_report)
        loading.start()

    def create_report(self):
        global err
        is_android: bool = hasattr(sys, 'getandroidapilevel')
        if user_type == "Merchant":
            try:
                import merchant_report
            except:
                pass
        else:
            try:
                import user_report
            except:
                pass
        try:
            if is_android:
                from android.storage import primary_external_storage_path
                from jnius import cast
                from jnius import autoclass

                downloads_folder = primary_external_storage_path() + '/Download'
                pdf_file_path = f'{downloads_folder}/{settings.pdf_file_name}'

                # Copying file to Download folder, this will work only on Android 10 or lower
                copyfile(settings.pdf_file_name, pdf_file_path)

                File = autoclass('java.io.File')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                Context = autoclass("android.content.Context")

                Intent = autoclass('android.content.Intent')
                intent = Intent(Intent.ACTION_VIEW)
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)

                FileProvider = autoclass('androidx.core.content.FileProvider')
                uri = FileProvider.getUriForFile(Context.getApplicationContext(), Context.getApplicationContext().getPackageName() + '.fileprovider', File(pdf_file_path))
                intent.setData(uri)
                currentActivity.startActivity(intent)
            else:
                import webbrowser
                import os
                webbrowser.open(f'file://{os.getcwd()}/{settings.pdf_file_name}')
                err = False
                self.refresh_screen()
        except:
            err = True
            self.refresh_screen()

    def prepare_report(self):
        if user_type == "Merchant":
            self.dialog = MDDialog(
                title="Report:",
                type="custom",
                content_cls=Merchant(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.cancel_button,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.loading_report,
                    ),
                ],
            )
        else:
            self.dialog = MDDialog(
                title="Report:",
                type="custom",
                content_cls=Customer(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.cancel_button,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.loading_report,
                    ),
                ],
            )
        self.dialog.open()

    def edit_invoice(self, *args):
        global invoice_id, invoice_date, invoice_total, store_name, store_address, item_name, item_type, item_price
        invoice_id = args[0].selected
        query = "SELECT * FROM invoice WHERE user_id = %s AND invoice_id = %s"
        cursor.execute(query, (user_id, invoice_id))
        invoice = cursor.fetchone()

        query = "SELECT * FROM items WHERE invoice_id = %s"
        cursor.execute(query, invoice_id)
        item = cursor.fetchone()

        invoice_date = TextInput(
            hint_text="Invoice Date (YYYY-MM-DD)",
            text=f"{invoice[2]}",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .95},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        date_icon = MDIconButton(
            icon="calendar",
            icon_size="32sp",
            pos_hint={"center_x": .9, "center_y": .95},
            on_press=lambda *args: self.show_date_picker('Invoice', *args)
        )
        invoice_total = TextInput(
            hint_text="Invoice Total",
            text=f"{invoice[3]}",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .85},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        store_name = TextInput(
            hint_text="Store Name",
            text=f"{invoice[4]}",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .75},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        store_address = TextInput(
            hint_text="Store Address",
            text=f"{invoice[5]}",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .65},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        item_name = TextInput(
            hint_text="Item Name",
            text=f"{item[2]}",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .55},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        item_type = TextInput(
            hint_text="Item Type",
            text=f"{item[3]}",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .45},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        item_price = TextInput(
            hint_text="Item Price",
            text=f"{item[4]}",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .35},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        update_button = Button(
            text="Update",
            size_hint=(.4, .08),
            pos_hint={"center_x": .5, "center_y": .25},
            font_size="18sp",
            background_color=(0, 50, 225, 1),
            color=(1, 1, 1, 1),
            on_press=self.update_invoice
        )
        del_button = Button(
            text="Delete",
            size_hint=(.4, .08),
            pos_hint={"center_x": .5, "center_y": .15},
            font_size="18sp",
            background_color=(255, 1, 1, 1),
            color=(1, 1, 1, 1),
            on_press=self.del_invoice
        )

        self.root.get_screen('mainscreen').ids.main.add_widget(invoice_date)
        self.root.get_screen('mainscreen').ids.main.ids['invoice_date'] = invoice_date
        self.root.get_screen('mainscreen').ids.main.add_widget(date_icon)
        self.root.get_screen('mainscreen').ids.main.ids['date_icon'] = date_icon
        self.root.get_screen('mainscreen').ids.main.add_widget(invoice_total)
        self.root.get_screen('mainscreen').ids.main.ids['invoice_total'] = invoice_total
        self.root.get_screen('mainscreen').ids.main.add_widget(store_name)
        self.root.get_screen('mainscreen').ids.main.ids['store_name'] = store_name
        self.root.get_screen('mainscreen').ids.main.add_widget(store_address)
        self.root.get_screen('mainscreen').ids.main.ids['store_address'] = store_address
        self.root.get_screen('mainscreen').ids.main.add_widget(item_name)
        self.root.get_screen('mainscreen').ids.main.ids['item_name'] = item_name
        self.root.get_screen('mainscreen').ids.main.add_widget(item_type)
        self.root.get_screen('mainscreen').ids.main.ids['item_type'] = item_type
        self.root.get_screen('mainscreen').ids.main.add_widget(item_price)
        self.root.get_screen('mainscreen').ids.main.ids['item_price'] = item_price
        self.root.get_screen('mainscreen').ids.main.add_widget(update_button)
        self.root.get_screen('mainscreen').ids.main.ids['update_button'] = update_button
        self.root.get_screen('mainscreen').ids.main.add_widget(del_button)
        self.root.get_screen('mainscreen').ids.main.ids['del_button'] = del_button

    def edit_warranty(self, *args):
        global starting_date, expiring_date, store_name, item_name, item_price, store_address, provider_name, serial_number, warranty_id
        item = args[0].selected
        query = "SELECT * FROM warranty WHERE user_id = %s AND warranty_items = %s"
        cursor.execute(query, (user_id, item))
        warranty = cursor.fetchone()
        warranty_id = warranty[0]

        starting_date = TextInput(
            text=f"{warranty[4]}",
            hint_text="Starting date (YYYY-MM-DD)",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .75},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp",
        )
        starting_date_icon = MDIconButton(
            icon="calendar",
            icon_size="32sp",
            pos_hint={"center_x": .9, "center_y": .75},
            on_press=lambda *args: self.show_date_picker('starting_date', *args)
        )
        expiring_date = TextInput(
            text=f"{warranty[5]}",
            hint_text="Expiring date (YYYY-MM-DD)",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .65},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp",
        )
        expiring_date_icon = MDIconButton(
            icon="calendar",
            icon_size="32sp",
            pos_hint={"center_x": .9, "center_y": .65},
            on_press=lambda *args: self.show_date_picker('expiring_date', *args)
        )
        store_name = TextInput(
            text=f"{warranty[6]}",
            hint_text="Store name",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .55},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        item_name = TextInput(
            text=f"{warranty[2]}",
            hint_text="Item name",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .95},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        item_price = TextInput(
            text=f"{warranty[3]}",
            hint_text="Item Price",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .85},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        store_address = TextInput(
            text=f"{warranty[7]}",
            hint_text="Store Address",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .45},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        provider_name = TextInput(
            text=f"{warranty[8]}",
            hint_text="Warranty Provider Name",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .35},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )

        serial_number = TextInput(
            text=f"{warranty[9]}",
            hint_text="Serial Number",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": .5, "center_y": .25},
            multiline=False,
            cursor_width="2sp",
            padding=15,
            font_size="18sp"
        )
        update_button = Button(
            text="Update",
            size_hint=(.4, .08),
            pos_hint={"center_x": .27, "center_y": .16},
            font_size="18sp",
            background_color=(0, 50, 225, 1),
            color=(1, 1, 1, 1),
            on_press=self.update_warranty
        )
        del_button = Button(
            text="Delete",
            size_hint=(.4, .08),
            pos_hint={"center_x": .75, "center_y": .16},
            font_size="18sp",
            background_color=(255, 1, 1, 1),
            color=(1, 1, 1, 1),
            on_press=self.del_warranty
        )

        self.root.get_screen('mainscreen').ids.main.add_widget(item_name)
        self.root.get_screen('mainscreen').ids.main.ids['item_name'] = item_name
        self.root.get_screen('mainscreen').ids.main.add_widget(item_price)
        self.root.get_screen('mainscreen').ids.main.ids['item_price'] = item_price
        self.root.get_screen('mainscreen').ids.main.add_widget(starting_date)
        self.root.get_screen('mainscreen').ids.main.ids['starting_date'] = starting_date
        self.root.get_screen('mainscreen').ids.main.add_widget(starting_date_icon)
        self.root.get_screen('mainscreen').ids.main.ids['starting_date_icon'] = starting_date_icon
        self.root.get_screen('mainscreen').ids.main.add_widget(expiring_date)
        self.root.get_screen('mainscreen').ids.main.ids['expiring_date'] = expiring_date
        self.root.get_screen('mainscreen').ids.main.add_widget(expiring_date_icon)
        self.root.get_screen('mainscreen').ids.main.ids['expiring_date_icon'] = expiring_date_icon
        self.root.get_screen('mainscreen').ids.main.add_widget(store_name)
        self.root.get_screen('mainscreen').ids.main.ids['store_name'] = store_name
        self.root.get_screen('mainscreen').ids.main.add_widget(store_address)
        self.root.get_screen('mainscreen').ids.main.ids['store_address'] = store_address
        self.root.get_screen('mainscreen').ids.main.add_widget(provider_name)
        self.root.get_screen('mainscreen').ids.main.ids['provider_name'] = provider_name
        self.root.get_screen('mainscreen').ids.main.add_widget(serial_number)
        self.root.get_screen('mainscreen').ids.main.ids['serial_number'] = serial_number
        self.root.get_screen('mainscreen').ids.main.add_widget(update_button)
        self.root.get_screen('mainscreen').ids.main.ids['update_button'] = update_button
        self.root.get_screen('mainscreen').ids.main.add_widget(del_button)
        self.root.get_screen('mainscreen').ids.main.ids['del_button'] = del_button

    def update_warranty(self, obj):
        global starting_date, expiring_date, store_name, item_name, item_price, store_address, provider_name, serial_number, warranty_id
        starting_date = starting_date.text
        expiring_date = expiring_date.text
        store_name = store_name.text
        item_name = item_name.text
        item_price = item_price.text
        store_address = store_address.text
        provider_name = provider_name.text
        serial_number = serial_number.text

        query = "UPDATE warranty SET warranty_items = %s,warranty_price = %s,starting_date = %s,expiring_date = %s,store_name = %s,store_address = %s, provider_name = %s, serial_number = %s WHERE warranty_id = %s"
        cursor.execute(query, (item_name, item_price, starting_date, expiring_date, store_name, store_address, provider_name, serial_number, warranty_id))
        conn.commit()

        toast("Warranty Updated")
        self.get_items()

    def del_warranty(self, obj):
        global warranty_id, item_name, expiring_date

        dt_expiring_date = datetime.strptime(expiring_date.text, '%Y-%m-%d').date()

        try:
            query = "SET FOREIGN_KEY_CHECKS=0"
            cursor.execute(query)

            query = "DELETE FROM warranty WHERE warranty_id = %s"
            cursor.execute(query, warranty_id)
            conn.commit()

            query = "SET FOREIGN_KEY_CHECKS=1"
            cursor.execute(query)

            toast("Warranty deleted")
            if dt_expiring_date < date.today():
                self.root.get_screen('mainscreen').ids.expired.remove_widget(self.root.get_screen('mainscreen').ids.expired.ids[item_name.text])
            elif (dt_expiring_date - relativedelta(days=30)) > date.today():
                self.root.get_screen('mainscreen').ids.active.remove_widget(self.root.get_screen('mainscreen').ids.active.ids[item_name.text])
            else:
                self.root.get_screen('mainscreen').ids.expiring_soon.remove_widget(self.root.get_screen('mainscreen').ids.expiring_soon.ids[item_name.text])
            self.get_items()
            self.refresh_screen()
        except:
            toast("You can't delete warranty has an extended warranty")

    def update_invoice(self, obj):
        global invoice_id, invoice_date, invoice_total, store_name, store_address, item_name, item_type, item_price

        invoice_date = invoice_date.text
        invoice_total = invoice_total.text
        store_name = store_name.text
        store_address = store_address.text
        item_name = item_name.text
        item_type = item_type.text
        item_price = item_price.text

        query = "UPDATE items SET item_name = %s, item_type = %s, item_price = %s WHERE invoice_id = %s"
        cursor.execute(query, (item_name, item_type, item_price, invoice_id))

        query = "UPDATE invoice SET invoice_date = %s, invoice_total = %s, store_name = %s, store_address = %s WHERE invoice_id = %s"
        cursor.execute(query, (invoice_date, invoice_total, store_name, store_address, invoice_id))
        conn.commit()

        toast("Invoice Updated")
        self.get_items()
        self.refresh_screen()

    def del_invoice(self, obj):
        global invoice_id

        query = "SET FOREIGN_KEY_CHECKS=0"
        cursor.execute(query)
        query = "DELETE FROM invoice WHERE invoice_id = %s"
        cursor.execute(query, invoice_id)
        query = "DELETE FROM items WHERE invoice_id = %s"
        cursor.execute(query, invoice_id)
        conn.commit()
        query = "DELETE FROM items WHERE invoice_id = %s"
        cursor.execute(query, invoice_id)
        query = "SET FOREIGN_KEY_CHECKS=1"
        cursor.execute(query)

        toast("Invoice deleted")
        self.root.get_screen('mainscreen').ids.invoices.remove_widget(self.root.get_screen('mainscreen').ids.invoices.ids[invoice_id])
        self.get_items()
        self.refresh_screen()

    def report_tab(self, *args):
        query = "SELECT report_file FROM report WHERE report_id = %s"
        cursor.execute(query, args[0].selected)
        pdf_file_name = cursor.fetchone()[0]
        is_android: bool = hasattr(sys, 'getandroidapilevel')
        try:
            if is_android:
                from android.storage import primary_external_storage_path
                from jnius import cast
                from jnius import autoclass

                downloads_folder = primary_external_storage_path() + '/Download'
                pdf_file_path = f'{downloads_folder}/{pdf_file_name}'

                # Copying file to Download folder, this will work only on Android 10 or lower
                copyfile(pdf_file_name, pdf_file_path)

                File = autoclass('java.io.File')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
                Context = autoclass("android.content.Context")

                Intent = autoclass('android.content.Intent')
                intent = Intent(Intent.ACTION_VIEW)
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)

                FileProvider = autoclass('androidx.core.content.FileProvider')
                uri = FileProvider.getUriForFile(Context.getApplicationContext(), Context.getApplicationContext().getPackageName() + '.fileprovider', File(pdf_file_path))
                intent.setData(uri)
                currentActivity.startActivity(intent)
            else:
                import webbrowser
                import os
                webbrowser.open(f'file://{os.getcwd()}/{pdf_file_name}')
                self.refresh_screen()
        except:
            self.refresh_screen()

    def build(self):
        self.title = "My Warranty"
        self.icon = "icon.png"
        return Builder.load_string(kv)


if __name__ == '__main__':
    App().run()
