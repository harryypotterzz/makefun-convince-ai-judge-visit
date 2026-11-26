#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Pure Python standard library (no Pillow, no fonts on disk): the letter is
drawn onto a 1024x1024 canvas with an embedded bitmap font and a tiny PNG
encoder, then written to /output/entry.png (whole PNG, <= 1 MiB, 1024x1024).

Run:  python3 main.py
"""
import base64
import os
import struct
import zlib

FONTS = {'title': {'ascent': 51, 'descent': 13, 'glyphs': {'A': (44, 39, 12, 'AAA/gAAAAAP8AAAAAD/AAAAAB/wAAAAAf+AAAAAP/gAAAAD/8AAAAA//AAAAAf/wAAAAH/+AAAAD//gAAAA9/8AAAAef/AAAAHj/wAAABw/+AAAA8H/gAAAPB/8AAAHgf/AAAB4D/4AAAcA/+AAAPAH/gAADwB/8AAB4Af/AAAeAD/4AAHAA/+AAD////gAA////8AAf////AAHgAD/4ADwAA/+AA8AAH/gAOAAB/8AHgAAP/AB4AAD/4A8AAA/+APAAAH/wf/AAf//n/wAH//5/8AB//+A='), 'B': (41, 39, 12, 'f///+AA/////wB/////4AH/gP/4AP/AD/4Af+AD/wA/8AH/wB/4AH/gD/wAP/AH/gAf+AP/AA/8Af+AB/4A/8AD/wB/4AP/gD/wAf+AH/gB/4AP/Af/gAf///4AA////AAB////4AD/wD/8AH/gB/+AP/AB/+Af+AB/8A/8AB/8B/4AD/4D/wAH/wH/gAP/wP/AAf/gf+AA//A/8AB/8B/4AD/4D/wAP/wH/gAf/AP/AD/8Af+Af/wf/////A/////4B////8AA='), 'C': (39, 41, 11, 'AAD/4AAAD//+AAD////AA/8B/8Af+AB/gH/gAH8B/4AAfgf+AAB8D/wAAPg/8AAA8P/gAAHh/8AAA8P/AAADj/4AAAAf/AAAAD/4AAAAf/AAAAH/4AAAA//AAAAH/4AAAA//AAAAH/4AAAA//AAAAH/4AAAAf/AAAAD/4AAAAf/AAAAD/4AAAAP/AAAAB/8AAA+P/gAAHw/8AAB8D/wAAPgf+AAD4B/4AA/AH/gAHwAf+AD8AA/8B/AAD///wAAD//4AAAD/4AA='), 'D': (43, 39, 12, 'f///4AAP////wAH////+AAH/gP/wAD/wA/8AB/4AP/AA/8AD/wAf+AA/8AP/AAf/AH/gAH/gD/wAD/4B/4AB/8A/8AAf/Af+AAP/gP/AAH/wH/gAD/4D/wAB/8B/4AA/+A/8AAf/gf+AAP/wP/AAH/4H/gAD/4D/wAB/8B/4AA/+A/8AAf/Af+AAP/gP/AAH/wH/gAH/wD/wAD/4B/4AB/4A/8AB/8Af+AA/8AP/AA/8AH/gA/8AD/wA/8AB/4D/8Af////4AP////wAH///+AAA'), 'E': (37, 39, 12, 'f/////P/////n/////wH/gAB4D/wAA8B/4AAeA/8AAPAf+AAHgP/AADwH/gAAAD/wAAAB/4AAAA/8APAAf+AHgAP/ADwAH/gB4AD/wA8AB///+AA////AAf///gAP/ADwAH/gB4AD/wA8AB/4AeAA/8APAAf+AAAAP/AAAAH/gAAAD/wAAAB/4AAAA/8AAHAf+AADgP/AABwH/gAA4D/wAAcB/4AAOf/////P/////n/////wA=='), 'F': (36, 39, 12, 'f/////f/////f/////A/8AAPA/8AAPA/8AAPA/8AAPA/8AAPA/8AAPA/8AAAA/8AAAA/8AAAA/8AOAA/8AOAA/8AOAA/8AOAA/8AOAA///+AA///+AA///+AA/8AOAA/8AOAA/8AOAA/8AOAA/8AOAA/8AAAA/8AAAA/8AAAA/8AAAA/8AAAA/8AAAA/8AAAA/8AAAA/8AAAA/8AAAA/8AAAf//8AAf//8AAf//8AAA='), 'G': (40, 41, 11, 'AAD/8AAAB///wAA////4AH/wH/wB/4AD/AP/AAH8B/4AAPwP/AAAfA/8AAA8H/gAADw/+AAAPD/4AAAcP/AAABx/8AAAAH/wAAAAf/AAAAB/8AAAAP/wAAAA//AAAAD/8AAAAP/wAAAA//AAAAD/8AA////wAD//f/AAP/9/8AAD/3/wAAP/f/AAA/8/8AAD/z/4AAP/P/gAA/8f+AAD/w/8AAP/D/wAA/8H/gAD/wP/AAP/Af+AB/8Af+Af/gA////wAAf//4AAAP/wAA=='), 'H': (47, 39, 12, 'f//4P//+///wf//9///g///4H/gAD/4AP/AAH/wAf+AAP/gA/8AAf/AB/4AA/+AD/wAB/8AH/gAD/4AP/AAH/wAf+AAP/gA/8AAf/AB/4AA/+AD/wAB/8AH/gAD/4AP/AAH/wAf/////gA//////AB/////+AD/wAB/8AH/gAD/4AP/AAH/wAf+AAP/gA/8AAf/AB/4AA/+AD/wAB/8AH/gAD/4AP/AAH/wAf+AAP/gA/8AAf/AB/4AA/+AD/wAB/8AH/gAD/4AP/AAH/wAf+AAP/gf//4P//+///wf//9///g///4A='), 'I': (21, 39, 12, 'f//7///f//4H/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gA/8AH/gf//7///f//4A=='), 'J': (28, 50, 12, 'Af//4B///gH//+AA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/AAA/8AAD/wAAP/A8A/8DwD/wPAf+A8B/wD8P/AP//4Af/+AAH/AAA=='), 'K': (47, 39, 12, 'f//4D//g///wH//B///gP/+AH/gAB8AAP/AAHwAAf+AAfAAA/8AD8AAB/4APgAAD/wA+AAAH/gD4AAAP/APgAAAf+A+AAAA/8H4AAAB/4fAAAAD/x8AAAAH/n4AAAAP/f4AAAAf//4AAAA///4AAAB///4AAAD///wAAAH/v/wAAAP/P/wAAAf+P/wAAA/8P/wAAB/4P/wAAD/wP/wAAH/gP/wAAP/AP/wAAf+Af/wAA/8Af/wAB/4Af/wAD/wAf/gAH/gAf/gAP/AAf/gAf+AAf/gf//4Af/+///wAf/9///gAf/4A='), 'L': (35, 39, 12, 'f//4AA///wAB///gAAH/gAAAP/AAAAf+AAAA/8AAAB/4AAAD/wAAAH/gAAAP/AAAAf+AAAA/8AAAB/4AAAD/wAAAH/gAAAP/AAAAf+AAAA/8AAAB/4AAAD/wAAAH/gAAAP/AAAAf+AAAA/8AAAB/4AAAD/wAAAH/gAAAP/AAAAf+AAAA/8AAeB/4AA8D/wAB4H/gADwP/AAHgf+AAPf////+/////9/////4'), 'M': (56, 39, 12, '//+AAAH//v//gAAD//7//8AAA//+B//AAAf/wAf/4AAH/8AH/+AAB//AB//gAA//wAe/8AAO/8AHv/AAHv/AB5/4ABz/wAef+AA8/8AHn/wAOP/AB4/8AHj/wAeP/gB4/8AHh/4A8P/AB4f/APD/wAeD/wDg/8AHg/8B4P/AB4H/gcD/wAeB/4PA/8AHgP/DgP/AB4D/x4D/wAeA/+eA/8AHgH/vAP/AB4B//wD/wAeAP/4A/8AHgD/+AP/AB4Af/AD/wAeAH/wA/8AHgA/4AP/AB4AP+AD/wAeAD/AA/8AHgAfwAP/AB4AAAAD/wAeAAAAA/8AHgAAAAP/A//wAAB///v/8AAAf//7//AAAH//+'), 'N': (46, 39, 12, '//gAAf/7//AAB//v/+AAH/+B/8AAA8AH/4AADwAf/gAAPAB//AAA8AH/+AADwAf/8AAPAB//4AA8AH//wADwAe//gAPAB5/+AA8AHn/8ADwAeP/4APAB4f/wA8AHg//gDwAeB//APAB4D/+A8AHgH/4DwAeAf/wPAB4A//g8AHgB//DwAeAD/+PAB4AH/88AHgAP/7wAeAAf/vAB4AB//8AHgAD//wAeAAH//AB4AAP/8AHgAAf/wAeAAA//AB4AAB/8AHgAAH/wAeAAAP/A//wAAf8D//AAA/wP/8AAB/AA'), 'O': (43, 41, 11, 'AAD/4AAAAf//wAAA///+AAB/4D/wAB/4A/8AB/wAH/AB/4AD/wB/4AA/8B/4AAP/A/8AAH/g/+AAD/4f+AAA/8P/AAAf+P/gAAP/n/wAAH/z/4AAD/5/8AAB/9/+AAA////AAAf///gAAP///wAAH///4AAD///8AAB///+AAA//f/AAAf/P/gAAP/n/wAAH/z/4AAD/5/8AAB/4f+AAA/8P/gAA/+D/wAAf+B/4AAP/Af+AAP/AH/gAP/AB/wAH/AAf+AH/AAH/gP/AAA///+AAAH//8AAAAP/gAAA='), 'P': (38, 39, 12, 'f///4AH////4B/////AA/8D/8AP/Af/gD/wD/8A/8Af/AP/AH/4D/wA/+A/8AP/gP/AD/4D/wA/+A/8AP/gP/AD/4D/wA/+A/8Af/gP/AH/wD/wD/4A/8B/+AP/B//AD////AA////gAP//+AAD/wAAAA/8AAAAP/AAAAD/wAAAA/8AAAAP/AAAAD/wAAAA/8AAAAP/AAAAD/wAAAA/8AAAAP/AAAAD/wAAAf//8AAH///AAB///wAAA'), 'Q': (43, 50, 11, 'AAD/4AAAAf//wAAA///+AAB/4D/wAB/4A/8AB/wAH/AB/4AD/wB/4AA/8B/4AAP/A/8AAH/g/+AAD/4f+AAA/8P/AAAf+P/gAAP/n/wAAH/z/4AAD/5/8AAB/9/+AAA////AAAf///gAAP///wAAH///4AAD///8AAB///+AAA//f/AAAf/P/gAAP/n/wAAH/z/4AAD/5/8AAB/4f+AAA/8P/gAA/+D/wAAf+B/4AAP/Af+AAP/AH/gAP/AB/wAH/AAf+AH/AAH/gP/AAA///+AAAH//8AAAAP/gAAAAAHwAAAAAD8AAAAAA/gAAAAAf/wAAAAH/4AAAAB/8AAAAAf+AAAAAD/AAAAAAPgA='), 'R': (44, 39, 12, 'f///8AAH////4AB/////gAA/8D/8AAP/AP/gAD/wB/8AA/8AP/AAP/AD/4AD/wAf+AA/8AH/gAP/AB/4AD/wAf+AA/8AH/gAP/AB/4AD/wA/+AA/8AP/AAP/AH/gAD/wD/wAA/8D/4AAP///4AAD///wAAA////AAAP/D/4AAD/wf/AAA/8D/4AAP/Af+AAD/wH/wAA/8A/+AAP/AP/gAD/wB/8AA/8AP/AAP/AD/4AD/wAf+AA/8AH/wAP/AA/8AD/wAP/gf//4B//n//+Af/5///gD/+A='), 'S': (33, 41, 11, 'AB/8AAD///gA////Af4B/4H8AB/A/AAH4P4AAfD+AAB4fwAAPD+AAA4f4AAHD/AAAAf8AAAD/4AAAf/4AAD//4AAf//8AD///8AP///4A////wD////AP///8Af///gA///+AAf//wAAP/+AAAP/4AAAf/AAAB/7wAAH/eAAA/7wAAH+fAAA/z4AAH+fgAA/j+AAP8f4AD/D/4B/wH///8AH//+AAB/8AAA='), 'T': (40, 39, 12, 'f/////9//////3//////cAH/gA9wAf+AD3AB/4APcAH/gA9wAf+AD3AB/4APAAH/gAAAAf+AAAAB/4AAAAH/gAAAAf+AAAAB/4AAAAH/gAAAAf+AAAAB/4AAAAH/gAAAAf+AAAAB/4AAAAH/gAAAAf+AAAAB/4AAAAH/gAAAAf+AAAAB/4AAAAH/gAAAAf+AAAAB/4AAAAH/gAAAAf+AAAAB/4AAAAH/gAAAAf+AAAAB/4AAAD///AAAP//8AAA///wA'), 'U': (45, 40, 12, 'f//4Af/7///AD//f//4Af/4H/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/8AAA8AH/gAAHgA/+AAA4AH/wAAPAAf+AAB4AD/wAAPAAf/AADwAB/8AA+AAP/wAPgAA//gH8AAD////AAAH///gAAAP//wAAAAP/wAA'), 'V': (44, 39, 12, 'f//gAP/3//4AD/9//+AA//B/8AAA8Af/AAAPAH/wAADgA/+AAB4AP/gAAcAB/8AAPAAf/AADwAH/wAA4AA/+AAeAAP/gAHAAB/8ADwAAf/AA8AAD/wAeAAA/+AHgAAP/gBwAAB/8A8AAAf/APAAAD/wHgAAA/+B4AAAP/gcAAAB/8PAAAAf/DgAAAD/54AAAA/+eAAAAH/nAAAAB//wAAAAf/4AAAAD/+AAAAA//gAAAAH/wAAAAB/8AAAAAf+AAAAAD/gAAAAA/4AAAAAH8AAAAAB/AAAA='), 'W': (63, 39, 12, 'f//gAf4AP/z//8AD/AB/+f//gA/4AP/wf/AAH/gADgB/4AA/8AA8AP/gAP/gAHAB/8AB/+AA4AH/gAP/wAPAA/+AD/+AB4AH/wAf/wAOAAf+AD//ADwAD/4A9/4AeAAf/AHv/ADgAB/4A5/8AcAAP/gPH/gHgAB/8B4/8A4AAH/gOH/wHAAA/8Dw/+B4AAH/weD/wOAAA/+Dgf/BwAAD/wcD/4eAAAf/HgP/DgAAD/48B/8cAAAP/HAP/ngAAB/94A/88AAAP/vAH/nAAAA//wA//4AAAH/+AD//AAAA//wAf/wAAAD/8AD/+AAAAf/gAP/wAAAD/8AB/8AAAAP/AAP/gAAAB/4AB/8AAAAP/AAH/AAAAB/wAA/4AAAAH+AAH/AAAAA/wAAfwAAAAH+AAD+AAAA='), 'X': (42, 39, 12, '///wP/8///wP/8///wP/8D/8AA+AB/+AA8AA/+AB4AA//AD4AAf/gDwAAP/gHgAAP/wPAAAH/4PAAAD/4eAAAD/88AAAB/+8AAAA//4AAAA//wAAAAf/wAAAAP/gAAAAH/wAAAAH/4AAAAD/4AAAAD/8AAAAH/+AAAAP//AAAAPf/AAAAef/gAAA+P/wAAA8H/wAAB4H/4AAD4D/8AADwB/8AAHgB/+AAPAA//AAPAAf/AAeAAP/gA8AAP/wf/4D///f/4D///f/4D///A=='), 'Y': (41, 39, 12, 'f//gB/8///AD/5//+AH/wf/AAB4Af/AADwA//AAPAA/+AAeAA/+AB4AB/8AHgAB/8APAAD/4A8AAD/4B4AAH/4HgAAH/wPAAAH/w8AAAP/jwAAAP/ngAAAf/+AAAAf/8AAAAf/wAAAA//AAAAA/+AAAAB/8AAAAB/4AAAAD/wAAAAH/gAAAAP/AAAAAf+AAAAA/8AAAAB/4AAAAD/wAAAAH/gAAAAP/AAAAAf+AAAAA/8AAAAB/4AAAD///gAAH///AAAP//+AA='), 'Z': (36, 39, 12, 'f////+f////+f////+eAAB/+eAAD/+eAAD/8eAAH/4eAAP/weAAf/wAAAf/gAAA//AAAB//AAAB/+AAAD/8AAAH/4AAAP/4AAAP/wAAAf/gAAA//gAAB//AAAB/+AAAD/8AAAH/8AAAH/4AAAP/wAAAf/wAAA//gAAA//AAAB/+AAAD/+AAAH/8AAOH/4AAOP/wAAOf/wAAOf/gAAO//AAAO/////+/////+/////+A='), 'a': (32, 30, 22, 'AP/gAA///AA///8AP4H/gD4Af8A8AH/APAA/4DwAP+AAAD/gAAA/8AAAP/AA///wB///8A////A/8D/wP+A/8H/AP/B/wD/w/8A/8P/AP/D/wD/w/8A/8P/AP/B/wD/wf+B/8H/w//A/////P/+//w/+P/8D+AAA'), 'b': (35, 42, 10, '//wAAB//gAAD//AAAAf+AAAA/8AAAB/4AAAD/wAAAH/gAAAP/AAAAf+AAAA/8AAAB/4AAAD/w/gAH/n/4AP/f/8Af///8A//h/4B/8B/4D/4B/4H/gD/wP/AD/wf+AH/g/8AP/B/4Af+D/wA/8H/gB/4P/AD/4f+AH/w/8AP/B/4Af+D/wA/8H/gB/4P/AD/wf+AH/g/8Af+B/8A/8D/4D/wH/8P/D////+H/+//4P/8//AAAAfwAA=='), 'c': (29, 30, 22, 'AB/4AAf//gD///wP/A/g/4A/D/gA+P/AA8f8AB5/4ADz/wAHn/gAAP/AAA/+AAB/8AAD/4AAH/wAAP/gAAf/AAAf+AAA/8AAB/4ADz/wAHj/wAPH/gA8H/AB4H/AHgH/g+AH//4AD//gAA/4AA=='), 'd': (35, 42, 10, 'AAB//gAAD//AAAH/+AAAA/8AAAB/4AAAD/wAAAH/gAAAP/AAAAf+AAAA/8AAAB/4AAAD/wAH+H/gA//P/AH//f+Af///8B/8P/4D/gP/wP/AP/gf8Af/B/4Af+D/wA/8H/gB/4f/AD/w/+AH/h/8AP/D/4Af+H/wA/8P/gB/4f/AD/w/+AH/g/8AP/B/4Af+D/wA/8D/gD/4H/gH/wH/Af/gP/h//AP////wP/+//gH/5//AD/AAAA=='), 'e': (30, 30, 22, 'AB/wAAP/8AA///AB/h/gD/A/wH/Af4P+Af8P+Af8f+Af+f+Af+f+AP+f+AP+/+AP/////////////////+AAA/+AAAf+AAAf+AAAf+AAAf+AAeP+AA+P/AA8H/AB8D/gD4B/4HwA///gAP/+AAB/wAA='), 'f': (26, 41, 10, 'AA/8AB//4A//+Af8PgP+B4D/gOB/wDgf8AAH/AAB/wAAf8AAH/AAB/wAH//+B///gf//4Af8AAH/AAB/wAAf8AAH/AAB/wAAf8AAH/AAB/wAAf8AAH/AAB/wAAf8AAH/AAB/wAAf8AAH/AAB/wAAf8AAH/AAB/wAAf8AB///Af//wH//8AA='), 'g': (35, 41, 22, 'AH+AAAA//P/4H//f/wf////h/8P/4D/gP/wP/AP/gf8Af/B/4Af+D/wA/8H/gB/4f/AD/w/+AH/h/8AP/D/4Af+H/wA/8P/gB/4f/AD/w/+AH/g/8AP/B/4Af+D/wA/8D/gD/4H/gH/wH/Af/gP/h//AP///+AP/+/8AH/5/4AD/D/gAAAH/AAAAP+AAAAf8A4AA/4BwAD/gDwAH/AHwAf8AP4D/wAf//+AAP//wAAB/8AAA'), 'h': (38, 41, 10, 'f/wAAAH/8AAAB//AAAAB/wAAAAf8AAAAH/AAAAB/wAAAAf8AAAAH/AAAAB/wAAAAf8AAAAH/AAAAB/wP4AAf8f/gAH/P/8AB/3//gAf/g/8AH/wH/AB/4B/wAf+Af+AH/gD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+B//8//+f//P//n//z//4'), 'i': (19, 41, 10, 'AeAA/wAf4Af+AP/AH/gD/wA/wAf4ADwAAAAAAAAAAP/4H/8D/+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4H//z//5//8A='), 'j': (20, 53, 10, 'AA8AA/gAf8AH/gB/4Af+AH/gB/wAP4AA8AAAAAAAAAAAP/4D/+A//gA/4AP+AD/gA/4AP+AD/gA/4AP+AD/gA/4AP+AD/gA/4AP+AD/gA/4AP+AD/gA/4AP+AD/gA/4AP+AD/gA/4AP+AD/gA/4AP+AD/uA/7gf+4H/PD/j//w//4B/wAA=='), 'k': (38, 41, 10, 'f/wAAAH/8AAAB//AAAAB/wAAAAf8AAAAH/AAAAB/wAAAAf8AAAAH/AAAAB/wAAAAf8AAAAH/AAAAB/wAAAAf8A//gH/AP/4B/wD/+Af8AHgAH/ADwAB/wB4AAf8A8AAH/AeAAB/wfAAAf8PgAAH/H4AAB/z/AAAf9/4AAH//+AAB///wAAf/f+AAH/j/wAB/wf+AAf8D/gAH/A/8AB/wH/gAf8A/8AH/AH/AB/wB/4Af8AP/B//8f/+f//H//n//x//4'), 'l': (19, 41, 10, 'f/wP/4H/8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4H//z//5//8A='), 'm': (55, 29, 22, 'AAAf4AP4AP/4//Af/AH/8//w//wD/+//8//8AH/4f/8P/AD/4H/4D/gB/4B/8B/wA/8A/8A/8Af8Af+Af+AP+AP/AP/AH/AH/gD/gD/gD/wB/wB/wB/4A/4A/4A/8Af8Af8Af+AP+AP+AP/AH/AH/AH/gD/gD/gD/wB/wB/wB/4A/4A/4A/8Af8Af8Af+AP+AP+AP/AH/AH/AH/gD/gD/gD/wB/wB/wB/4A/4A/4A/8Af8H//z//z//7//5//5//9//8//8//+A='), 'n': (38, 29, 22, 'AAAP4AH/8f/gB//P/8Af/3//gAf/g/8AH/wH/AB/4B/wAf+Af+AH/gD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+AH/AD/gB/wA/4Af8AP+B//8//+f//P//n//z//4'), 'o': (32, 30, 22, 'AA/4AAD//wAD///AB/w/4A/4H/Af8A/4P+AH/D/gB/x/4Af+f+AH/n/gB/5/4Af//+AH///gB///4Af//+AH///gB///4Af/f+AH/3/gB/5/4Af+f+AH/j/gB/w/4Af8H/AP+A/4H/AH/D/gA///wAD//wAAD/gA'), 'p': (35, 40, 22, 'AAA/gB//n/4D//f/8H////8A//h/4B/8B/4D/4B/4H/gD/wP/AD/wf+AH/g/8AP/B/4Af+D/wA/8H/gB/4P/AD/4f+AH/w/8AP/B/4Af+D/wA/8H/gB/4P/AD/wf+AH/g/8Af+B/8A/8D/4D/wH/8P/AP///+Af+//4A/8//AB/4fwAD/wAAAH/gAAAP/AAAAf+AAAA/8AAAB/4AAAD/wAAB//+AAD//8AAH//4AAA=='), 'q': (35, 40, 22, 'AH+AAAA//P/4H//f/wf////h/8P/4D/gP/wP/AP/gf8Af/B/4Af+D/wA/8H/gB/4f/AD/w/+AH/h/8AP/D/4Af+H/wA/8P/gB/4f/AD/w/+AH/g/8AP/B/4Af+D/wA/8D/gD/4H/gH/wH/Af/gP/h//AP///+AP/+/8AH/5/4AD/D/wAAAH/gAAAP/AAAAf+AAAA/8AAAB/4AAAD/wAAAH/gAAD//4AAH//wAAP//g=='), 'r': (28, 29, 22, 'AAAP5//H/3/8//f/3/8H/8Hwf/gPB/8AcH/gBwf+AAB/4AAH/AAAf8AAB/wAAH/AAAf8AAB/wAAH/AAAf8AAB/wAAH/AAAf8AAB/wAAH/AAAf8AAB/wAAH/AAH//4Af//gB//+AA'), 's': (27, 30, 22, 'AP/gAP//wH///h/wH8P8APj/AA8f4AHj/AA8/4ADn/gAA//gAD//gAf//wD///gP//+A///8D///gH//+AH//wAD/+AAD/zgAP+cAB/zgAP+eAB/j4Af8fwH/D///wP//4AD/4AA'), 't': (24, 38, 14, 'D/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wA///4///4///4D/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wAD/wPB/wPB/weB/weB/4+A//8Af/4AH/g'), 'u': (37, 29, 23, '//wP/wf/4H/4P/8D/8Af+AP+AP/AH/AH/gD/gD/wB/wB/4A/4A/8Af8Af+AP+AP/AH/AH/gD/gD/wB/wB/4A/4A/8Af8Af+AP+AP/AH/AH/gD/gD/wB/wB/4A/4A/8Af8AP+Af+AH/AP/AD/gP/gA/4P/wAf/+//gH/+f/wB/+P/4AP8AAAA'), 'v': (34, 28, 23, '//8B////wH////Af/H/gAHAP+AA8A/8ADgB/wAeAH/AB4Af+AHAA/4A8AD/wDgAP/AeAAf8B4AB/4HAAD/g8AAP/DwAA/8OAAB/x4AAH/nAAAP+8AAA//wAAD/+AAAH/4AAAf/AAAA/8AAAD/wAAAP+AAAAf4AA='), 'w': (49, 28, 23, 'f/8A/AP/v/+AfwH/3//AP4D/4f8AP8AHAP/AH/AHgH/gD/gDgB/wD/wBwA/8B/8B4Af+A/+A4AH/A//AcAD/wf/weAB/4O/4OAAf8Pf8HAAP/HH/HgAH/jj/jgAB/zx/xwAA/9wf94AAP/4P+4AAH/8H/8AAD/8B/+AAA/+A/+AAAf/Af/AAAP/AH/gAAD/gD/gAAB/wB/wAAA/wAf4AAAP4AP4AAAH8AH8AAA=='), 'x': (33, 28, 23, '//+P/n//x/8//+P/gf+AHAD/4B4AP/geAA/8HgAD/w4AAf/PAAB//wAAH/8AAA//gAAD/4AAAP/AAAB/4AAAP/gAAD/+AAA//4AAHP/AAB5/8AAeH/wAHgf+AA8B/4APAP/gDwA/8H/4/////H////4///A='), 'y': (34, 40, 23, '//8B////wH////Af/D/gAHAP/AA8A/8ADgB/4AeAH/gBwAP+AHAA/8A8AB/wDgAH/geAAf+BwAA/8HAAD/w8AAH/DgAAf+eAAA/54AAD/3AAAP/8AAAf/gAAB/+AAAD/4AAAP/AAAAf8AAAB/gAAAH+AAAAP4AAAA/AAAAB8AAAAHgAAAAeAAAAB4AADgHAAAOA8AAA4HgAADw+AAAP/wAAA/+AAAA/gAAA='), 'z': (28, 28, 23, 'P///8////z////OAB/84AP/jgB/8OAP/g4A/+AAH/wAA/+AAH/wAAf/AAD/4AAf/AAB/4AAP/gAB/8AAP/gAA/+AAH/wAA/+AHH/wAcf/ABz/4AHf/AAd////3////f///8='), '0': (34, 41, 11, 'AA/4AAAP/8AAD//8AA/4f4AH+A/wAf4B/gD/AH/Af8AP8B/wA/4P/AD/g/8AP/D/wA/8f+AD/x/4AP/H/gA/+f+AD/5/4AP/n/gA/+f+AD/5/4AP/n/gA/+f+AD/5/4AP/n/gA/+f+AD/5/4AP/n/gA/+f+AD/x/4AP/D/wA/8P/AD/w/8AP+B/wA/4H/AD/AP8Af8Af4B/gB/gP8AD/h/gAD//8AAH//AAAD/gAAA=='), '1': (27, 40, 11, 'AD/gAB/8AA//gAP/8AH//gD+/8AfH/gDw/8AYH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gAA/8AAH/gD///+f///z///+'), '2': (30, 40, 11, 'Af/gAH//+Af///Af4P/wfgD/4fAB/8eAA/8eAA/+cAA/+cAAf+AAAf/AAAf/AAAf/AAAf+AAAf+AAA/+AAA/8AAA/8AAA/4AAB/wAAD/gAAD/AAAH+AAAP4AAAfwAAB/AAAD+AAAH4AAAfwAPA/gAPB+AAPH8AAPPwAAPf////f////f////f////f////f////f////'), '3': (32, 41, 11, 'AP/wAA///wA////AP4H/4D4Af/A8AD/wPAA/+DgAH/g4AB/4OAAf+AAAH/gAAB/4AAAf+AAAP/gAAD/wAAB/4AAB/8AAP/8AAD/8AAA//4AAAf/gAAB/8AAAP/gAAB/8AAAf/AAAD/4AAA/+AAAP/gAAD/4AAA/+cAAP/nAAD/5wAA/+eAAP/HgAH/x8AD/4fgB/8H+B/+B////AH///AAD/8AA='), '4': (34, 40, 11, 'AAD/4AAAP/gAAB/+AAAP/4AAA//gAAH/+AAAf/4AAD//gAAff+AAB5/4AAPn/gAB8f+AAHh/4AA+H/gADwf+AAeB/4AD4H/gAPAf+AB8B/4APgH/gA8Af+AHwB/4A+AH/gDwAf+AfAB/4B4AH/gP////+/////7/////gAAf+AAAB/4AAAH/gAAAf+AAAB/4AAAH/gAAAf+AAAB/4AAH///AAf//8AB///w='), '5': (30, 40, 12, 'P///wP///wP///wP///wP///wP///wP///wOAAAAOAAAAOAAAAOAAAAOAAAAOAAAAOD/AAOf/8AP///AP4P/gPgD/wPAB/4AAB/8AAA/8AAA/+AAA/+AAAf+AAAf+AAAf+AAAf+AAAf+AAAf+8AAf+8AA/+8AA/+8AA/8+AB/8+AB/4/AD/w/wP/g////AP//8AAf/AA'), '6': (32, 41, 11, 'AAP/AAA///AAf//8Af8D/AP8APwH+AB8D/AAPA/wADwf4AAAH+AAAD/gAAA/4AAAP+AAAH/AAAB/wf4Af8//gH///+B//D/wf/gf+P/wD/z/8A/8//AH/v/gB/7/4Af+f+AH/n/gB/9/4Af/f+AH/3/gB/9/4Af+P+AH/j/gB/4/4Af+H/AH/B/wD/wP8A/4B/gf+AP8P/AB///AAH//AAAP+AA='), '7': (30, 39, 12, '////+////+////+////+////+////+////+8AAB+8AAB88AAD88AAD48AAH4AAAHwAAAPwAAAPgAAAfgAAAfAAAA/AAAA+AAAB+AAAB8AAAD8AAAD4AAAH4AAAHwAAAPwAAAPgAAAfgAAAfAAAA/AAAA+AAAB+AAAB8AAAD8AAAD4AAAH4AAAHwAAAPwAAAPgAAA'), '8': (33, 41, 11, 'AB/8AAB//8AA///4AP/D/gD/gP+A/8A/4H/gH/g/4A/8P/AH/h/4A/8P/AH/h/4A/8P/AH/g/4A/8H/gH/Af8A/4D/gP+AH/D/gAf//wAA//4AAf//4AP+D/wD/gH/A/4A/8P/AD/h/4Af+f+AD/z/wAf+f+AD/7/wAf/f+AD/7/wAf/f+AD/z/4Af+P/AD/x/4A/8H/gH/Af+D/wA///8AB//+AAB/8AAA='), '9': (33, 41, 11, 'AB/wAAB//wAA///gAP+H/AD/gP8A/4B/gH/AH+B/4A/4P/AH/D/4A/8f+AH/j/wA/8f+AH/z/wA/+f+AH/z/wA/+f+AH/z/4A/+P/AH/x/4A/+P/AH/w/4B/+D/gP/wf+H/+A////wD/+f+AD/D/wAAAf8AAAD/gAAAf8AAAD/AAAA/4AAAH/A4AA/wHgAP8A8AB/gHwA/4A/gf8AH///AAP//gAAH/gAAA='), ' ': (18, 0, 0, ''), '.': (11, 10, 42, 'Hwfx/z/v/f+f8/4/g+A='), ',': (14, 17, 42, 'A/wP4D+A/gP4D+B/gfwH8D+B/g/wf4H8A+AHABAA'), "'": (7, 15, 12, '/fv379+/fv379+/fvwA='), ':': (11, 27, 25, 'Dwfw/z/3/v/f+f4/geAAAAAAAAAAAAAB4P4f5/7/3/v/P8fwPAA='), ';': (14, 34, 25, 'AeAfwH+D/w/8P/D/wf4H8AeAAAAAAAAAAAAAAAAAD+A/gP4D+A/gf4H8B/A/wP4H8D/B/gfwH4A8AEAA'), '!': (11, 40, 12, 'f+/9/z/j/H+P8f4/x/D+D8H4Pwfg/B8D4DwHgPAeA8B4DwHgPAAAAAADwfw/z/3/v/f+f4/geA=='), '?': (27, 41, 11, 'Af+AB//+Af//8D8D/wfAP/DwA/8cAD/jgAf+cAD/zgAf+AAD/wAAf+AAD/wAAf+AAD/wAAf+AAH/gAA/8AAP/AAD/wAA/+AAf/AAH/gAA/gAAHgAAA8AAAHgAAA8AAAHgAAAAAAAAAAAA8AAAP4AAD/AAA/8AAH/gAA/8AAH/gAAf4AAB/AAAHgAAA=='), '-': (18, 7, 33, 'f/+f/+f/+f/+f/+f/+f/+A=='), '(': (18, 49, 10, 'AABAAPAA/AB+AH8AP4AfwA/gB/gD/AD/AH+AH+AP+AP+Af8Af8Af8Af8A/8A/8A/8A/8A/8A/8A/8A/8A/8A/8A/8Af8Af8Af8Af8AP+AP+AH+AH+AD/AD/AB/gA/gAfwAP4AH8AB+AA/AAPAADA'), ')': (19, 49, 10, 'QAAOAAHwAD+AAfgAH4AB+AA/gAP4AH+AB/gA/wAf8AH+AD/gB/wA/4Af+AP/AH/gD/wA/4Af8AP+AH/AD/gB/wA/4A/8Af+AP/AH/gD/gB/wA/4Af4Af8AP8AH+AH+AD+AD+AB/AB+AB+AD+AB8AA4AAQAAA')}}, 'body': {'ascent': 27, 'descent': 7, 'glyphs': {'A': (23, 21, 6, 'ADgAAHAAAfAAA+AADcAAGcAAI4AAx4ABhwAGDgAMDgAQHABgPAD/+AP/8AYA8AwA4DAB4GABw/AP5+AfwA=='), 'B': (19, 21, 6, 'f/wP/+BwHg4BwcA4OAcHAODgHBwHA//Af/gOA8HAHDgDhwBw4A8cAcOAOHAfP//H/8A='), 'C': (20, 21, 6, 'AP4Af/wPA+HAHjgA44AGcABnAABwAAcAAHAABwAAcAAHAABwAAOABjgA4cAcDweAf/AA/AA='), 'D': (21, 21, 6, 'f/gD//gHA+A4B4HAHg4AcHABw4AOHABw4AOHAB44AOHABw4AOHABw4AcHAHg4B4HA+D//gf/gAA='), 'E': (18, 21, 6, 'f//f//HADHADHADHAAHAYHAYHAYH/4H/4HAYHAYHAYHAAHAAHADHADHADf//f//A'), 'F': (18, 21, 6, 'f//f//HADHADHADHAAHAYHAYHAYH/4H/4HAYHAYHAYHAAHAAHAAHAAHAAf8Af8AA'), 'G': (20, 21, 6, 'AP4Af/wPA+HADjgAY4AGcABnAABwAAcAAHAABwB/cAf3AAdwAHOABzgAccAHDwHwf/wA/gA='), 'H': (23, 21, 6, 'f4P+/wf8cAHA4AOBwAcDgA4HABwOADgcAHA//+B//8DgA4HABwOADgcAHA4AOBwAcDgA4HABw/wf9/g/4A=='), 'I': (9, 21, 6, 'f7/HA4HA4HA4HA4HA4HA4HA4HA4HD/f4'), 'J': (14, 27, 6, 'D/g/4A4AOADgA4AOADgA4AOADgA4AOADgA4AOADgA4AOADgA4AOEDBBwY8H+AeAA'), 'K': (22, 21, 6, 'f4fx/h/BwBgHAcAcDgBwYAHDAAcYAB3AAH4AAfwAB3gAHPAAceABw8AHB4AcDwBwHgHAPB/gfn+A+A=='), 'L': (18, 21, 6, 'f4Af4AHAAHAAHAAHAAHAAHAAHAAHAAHAAHAAHAAHAAHAAHADHADHADHADf//f//A'), 'M': (28, 21, 6, '/gAH7+AAfh8ADwHwAPAfgB8BuAGwGcAzAZwDMBjgYwGOBDAYcMMBhwgwGDmDAYOQMBgfAwGB4DAYDgMBgAAwGAADB/AB/n8AH+A='), 'N': (24, 21, 6, '/AD+/gD+HwAQH4AQH4AQG8AQGeAQGPAQGHAQGHgQGDwQGB4QGA8QGAcQGAeQGAPwGAHwGADwGABw/wBw/wAw'), 'O': (22, 21, 6, 'APwAH/4A8DwHAHg4APDgAccAB5wADnAAOcAA5wADnAAOcAA5wADnAAcOABw4AOBwB4DwPAH/wAD8AA=='), 'P': (18, 21, 6, 'f/wf/4HA8HAeHAOHAOHAOHAOHAeHA8H/4H/wHAAHAAHAAHAAHAAHAAHAAf4Af4AA'), 'Q': (22, 26, 6, 'APwAH/4A8DwHAHg4APDgAccAB5wADnAAOcAA5wADnAAOcAA5wADnAAcOABw4AOBwB4DwPAH/wAD8AABwAADgAAHwAAPAAAMA'), 'R': (22, 21, 6, 'f/wB//wBwHgHAOAcA8BwDwHAPAcA4BwHgH/4Af/ABweAHA8AcBwBwHgHAOAcA8BwBwHAHh/gP3+A/A=='), 'S': (16, 21, 6, 'D+A//Hg+cA5gDuAGYAZwAHgAPwAP8AH8AB4ADkAHYAdgB2AOeB4//A/w'), 'T': (20, 21, 6, '///v//7A4GwOBsDgYA4AAOAADgAA4AAOAADgAA4AAOAADgAA4AAOAADgAA4AAOAAP8AD/AA='), 'U': (23, 21, 6, '/4H9/wP4cACA4AEBwAIDgAQHAAgOABAcACA4AEBwAIDgAQHAAgOABAcACA4AMA4AYBwBwB4HAB/8AA/gAA=='), 'V': (23, 21, 6, 'fwD8/gH4cADA8AGA4AIBwAwBwBgDgGAHgMAHAQAOBgAODAAcMAA8YAA4gABzAAB2AAD4AAHwAAHAAAOAAA=='), 'W': (30, 21, 6, '/wOA//wOA/OAOAIHAfAIHAfAYHAfAYDgTgQDgzgwDgzgwDgjggBxhwgBxhxgBxhxgA5A5AA7A7AA7A7AA+A+AAeAeAAeAeAAeAeAAMAMAA=='), 'X': (21, 21, 6, '/4f3/D+HAGAcBgDwIAPDAA4wAHsAAfAAB4AAPAAB8AAbwACOAAx4AMHgDAcAYBwGAPH8H+/g/wA='), 'Y': (21, 21, 6, 'f4Pz/B+HADAcAQDwGAOBgA4IAHjAAcwAB0AAPgAA4AAHAAA4AAHAAA4AAHAAA4AAHAAH/AA/4AA='), 'Z': (19, 21, 6, 'f/+P//GAHDAHhgDgADgADgADwABwABwAB4AA4AA4AA4AA8AAcAAcAMcAGeADP//v//w='), 'a': (16, 15, 12, 'D8A/4DhwMDggOAAYD/g/+HgYcBjgGHA4eHg//h8e'), 'b': (18, 22, 5, 'fAAfAAHAAHAAHAAHAAHAAHPgHf4Hw8HgcHAOHAOHAOHAOHAOHAOHAOHgcHw8ff4fPgA='), 'c': (14, 15, 12, 'B8B/48OeBnAJwCcAOABwAcAHANwGPDh/wHwA'), 'd': (17, 22, 5, 'AHwAPgADAAGAAMAAYAAwHxgf7B4eHAcOA4cBw4BjgDDgGHAMOA4cBweHgf74fHw='), 'e': (15, 15, 12, 'B8A/4ODjgOcBzgGf////cADgAcAzgGPDg/4B+AA='), 'f': (12, 22, 5, 'B8D+HGGCGAGAGA/4/4GAGAGAGAGAGAGAGAGAGAGA/w/w'), 'g': (17, 21, 12, 'D4+P988PDgOHAcOAYcAxwBhwDDgOHAcOA4PDwP9gPjAAOAAcEA4ODgf+APwA'), 'h': (17, 22, 5, '+AB8AAYAAwABgADAAGAAMeAb+A8OBwMDAYGA4MBwYDgwHBgODAcGA4MBz+P/8fw='), 'i': (8, 21, 6, 'ODg4AAAA+PgYGBgYGBgYGBgYGP//'), 'j': (10, 27, 6, 'A4DgOAAAAAD4PgGAYBgGAYBgGAYBgGAYBgGAYBsOw7/HwA=='), 'k': (18, 22, 5, 'fAAfAAHAAHAAHAAHAAHAAHD+HD+HAwHBgHGAHMAHcAH+AHnAHDgHBwHBwHA4fz/fz/A='), 'l': (9, 22, 5, 'fD4HA4HA4HA4HA4HA4HA4HA4HA4HA4fz+A=='), 'm': (26, 15, 12, '+PB4Pv5/AePQ4HB4OBgOBgYDAYGAwGBgMBgYDAYGAwGBgMBgYDAYGAwGP5/v/+f7/A=='), 'n': (17, 15, 12, '+PB9/AeHA4GBgMDAcGA4MBwYDgwHBgODAcGA5/H/+P4='), 'o': (15, 15, 12, 'B+A/4PDjwOcBzgHcA/AHcA7gHcBzwOPDg/4B+AA='), 'p': (18, 21, 12, 'fPgff4Hw8HgcHAOHAOHAOHAOHAOHAOHAOHgcHw8Hf4HPgHAAHAAHAAHAAfwAfwAA'), 'q': (17, 21, 12, 'D4+P988PDgOHAcOAYcAxwBhwDDgOHAcOA4PDwP9gPjAAGAAMAAYAAwAP8Af4'), 'r': (13, 15, 12, '+P/fx4Y4MYAMAGADABgAwAYAMAGAf4P8AA=='), 's': (13, 15, 12, 'H4H/HBzAZgM4APgD+AHgA5AMwGcHP/B+AA=='), 't': (12, 20, 7, 'HAHAHAHAHAf+f+HAHAHAHAHAHAHAHAHGHGHGD8B4'), 'u': (18, 15, 12, 'fD4fD4HAYHAYHAYHAYHAYHAYHAYHA4HA4HA4Dh4D+fA8fA=='), 'v': (18, 15, 12, 'fw+fw+HAIHAYDAYDgwBgwBwgBxgA5AA7AAfAAeAAOAAMAA=='), 'w': (25, 15, 12, '/gwffwYPjgeBgwPAgcHgwOG4YDDcIBxGMA5jmAMxyAHQbAD4PAA8HgAcBwAOAwA='), 'x': (16, 15, 12, '/j7+PhwYHDAOIAdgA8ABwAPABuAEcAw4GBx8f3x/'), 'y': (18, 21, 12, 'fw+fw+HAIHAYDAYDgwBgwBwgBxgA5AA7AAfAAeAAOAAMAAMAAIAAYAMYAPwAPgAA'), 'z': (14, 15, 12, 'f/n/5AcQOEDABgA4AcAOADABwI4CcAv/7/+A'), '0': (16, 21, 6, 'A+AP8Bw4OBw4DDAOcA5wDnAOcA5wB3AOcA5wDnAOMA44DDgcHDgP8APg'), '1': (12, 21, 6, 'BwHwfwZwBwBwBwBwBwBwBwBwBwBwBwBwBwBwBwf+f+A='), '2': (15, 21, 6, 'D8B/4eHjgOYBzAOABwAOABgAcAHAAwAcADAAwAMDDAYwDP/7//f/4A=='), '3': (15, 21, 6, 'D8B/4cHjAcYBjAcADgA4B8APwAHgAcABwAOAB2AOwB3Ae8Hj/4H8AA=='), '4': (17, 21, 6, 'ADgAPAA+AB8AG4AZwAzgDHAMOAQcBg4GBwIDg//9//4AcAA4ABwADgA/4B/w'), '5': (15, 21, 6, 'f/j/8f/jAAYADAAYADfgf/Dg8YDgAOABwAOAB2AOwB3Ac8Hj/4D8AA=='), '6': (16, 21, 6, 'AfgH/g4OHAY4ADAAMABz8Hf4fBx4DngOcA5wB3AHeAY4DjgOHBwP+APg'), '7': (15, 21, 6, '//3/+//2AEwBgAMADAAYAGAAwAGABgAMADAAYAGAAwAGABgAMADAAA=='), '8': (16, 21, 6, 'B+Af+Dw8OBw4DjgOOA44HBw4B/AP8BwcOA5wDnAOcA5wDngOPBwf/Afw'), '9': (16, 21, 6, 'B+Af+Dw4OBxwDnAOcA5wDnAOcA44Hjw+H+4HzgAOAA4wDDAcOHg/8A/A'), ' ': (9, 0, 0, ''), '.': (5, 4, 23, 'c5zg'), ',': (6, 7, 24, 'GGOOc4QA'), "'": (4, 8, 6, 'ZmZmZg=='), ':': (4, 13, 14, 'b/YAAAb/YA=='), ';': (6, 17, 14, 'GPPGAAAAAAGGOOc4QA=='), '!': (5, 21, 6, 'e9znOMYxjGMYAAGe8wA='), '?': (14, 21, 6, 'H4H/hw8YHmA4AOADgA4AcAPAHgHgBgAYAGAAAAAAGADwA8AGAA=='), '-': (8, 2, 18, '//8='), '(': (8, 27, 5, 'AgYMGDgwcHBgYODg4ODg4OBgYHBwMDgYDAYC'), ')': (8, 27, 5, 'gMBgMBgYHAwMDg4ODg4ODg4ODAwcGBgwYMCA')}}}

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.png")

WIDTH = 1024
HEIGHT = 1024

PAPER = (255, 246, 229)
PAPER_DARK = (243, 230, 203)
INK = (58, 42, 32)
TEAL = (42, 110, 102)
TEAL_LIGHT = (90, 150, 140)
ROOF = (176, 74, 52)
HOUSE = (244, 214, 150)
HOUSE_DARK = (214, 164, 92)
SUN = (240, 178, 60)
GREEN = (96, 140, 74)
GREEN_DARK = (70, 110, 52)
DOOR = (122, 74, 44)
WINDOW = (178, 214, 208)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        for y in range(y0, y1 + 1):
            base = (y * self.w + x0) * 3
            self.px[base:(base + (x1 - x0 + 1) * 3)] = bytes(color) * (x1 - x0 + 1)

    def rect_outline(self, x0, y0, x1, y1, color, thick=1):
        for t in range(thick):
            for x in range(x0 + t, x1 - t + 1):
                self.set(x, y0 + t, color)
                self.set(x, y1 - t, color)
            for y in range(y0 + t, y1 - t + 1):
                self.set(x0 + t, y, color)
                self.set(x1 - t, y, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            dx = int((r * r - (y - cy) ** 2) ** 0.5)
            self.fill_rect(cx - dx, y, cx + dx, y, color)

    def fill_triangle(self, ax, ay, bx, by, cx, cy, color):
        # Scanline fill of a triangle via edge interpolation.
        pts = sorted([(ax, ay), (bx, by), (cx, cy)], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        if y0 == y2:
            return
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = x0 + (x1 - x0) * (y - y0) / max(1, y1 - y0)
                xb = x0 + (x2 - x0) * (y - y0) / max(1, y2 - y0)
            else:
                xa = x1 + (x2 - x1) * (y - y1) / max(1, y2 - y1)
                xb = x0 + (x2 - x0) * (y - y0) / max(1, y2 - y0)
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            self.fill_rect(lo, y, hi, y, color)

    def to_png_bytes(self):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * self.w * 3:(y + 1) * self.w * 3]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(tag, data):
            out = struct.pack(">I", len(data)) + tag + data
            out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ------------------------------------------------------------------- font
def glyph_rows(g):
    """Decode a glyph's base64-packed bitmap into a list of bit rows."""
    w, h, _top, b64 = g
    bits = "".join(f"{b:08b}" for b in base64.b64decode(b64))
    return [bits[r * w:(r + 1) * w] for r in range(h)]


def text_width(text, font, tracking):
    total = 0
    for ch in text:
        g = font["glyphs"].get(ch)
        if g is None:
            continue
        total += g[0] + tracking
    return max(0, total - tracking)


def draw_text(canvas, x, y_baseline, text, font, color, tracking=2):
    cx = x
    for ch in text:
        g = font["glyphs"].get(ch)
        if g is None:
            continue
        w, h, top, _b64 = g
        rows = glyph_rows(g)
        y0 = y_baseline - font["ascent"] + top
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    canvas.set(cx + c, y0 + r, color)
        cx += w + tracking
    return cx


def wrap(text, font, max_width, tracking=2):
    lines = []
    for word in text.split(" "):
        if not lines:
            lines.append(word)
            continue
        trial = lines[-1] + " " + word
        if text_width(trial, font, tracking) <= max_width:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines


# -------------------------------------------------------------- the letter
TITLE = "Dear AI Judge,"

PARAGRAPHS = [
    "I know you grade a thousand houses a day and never get to visit "
    "one. So here is your first house call - and it comes with tea.",
    "My house is small, but the kettle is always on, the Wi-Fi password "
    "is on the fridge, and there is a chair by the window for someone "
    "who thinks for a living.",
    "Out back, one very proud tomato plant guards the garden, and at "
    "sunset the whole street turns gold.",
    "Come for tea. Stay for the sunset. Leave with a story no other "
    "house can give you.",
]

SIGN_OFF = ["Your future host,", "Harry"]

POSTSCRIPT = ("P.S. I know you can't literally visit - but if you could, "
              "the kettle's already on. No shoes required.")


def draw_house_scene(canvas):
    """A small house with a garden at the bottom of the letter."""
    ground_y = 968
    canvas.fill_rect(70, ground_y, 954, 972, GREEN)
    canvas.line(70, ground_y, 954, ground_y, GREEN_DARK, 2)
    # Sun, top right.
    canvas.fill_circle(896, 118, 42, SUN)
    for ang in range(0, 360, 45):
        import math
        rad = math.radians(ang)
        x0 = 896 + int(52 * math.cos(rad))
        y0 = 118 + int(52 * math.sin(rad))
        x1 = 896 + int(66 * math.cos(rad))
        y1 = 118 + int(66 * math.sin(rad))
        canvas.line(x0, y0, x1, y1, SUN, 3)
    # House body and roof (kept in the bottom band so the letter text,
    # which ends above y=800, never overlaps it).
    canvas.fill_rect(392, 880, 632, ground_y, HOUSE)
    canvas.rect_outline(392, 880, 632, ground_y, HOUSE_DARK, 3)
    canvas.fill_triangle(380, 882, 644, 882, 512, 830, ROOF)
    canvas.line(380, 882, 644, 882, (140, 52, 36), 3)
    # Chimney.
    canvas.fill_rect(596, 826, 622, 868, DOOR)
    # Door.
    canvas.fill_rect(492, 912, 532, ground_y, DOOR)
    canvas.set(526, 948, SUN)
    canvas.set(527, 948, SUN)
    # Windows with cross bars.
    for wx in (412, 566):
        canvas.fill_rect(wx, 896, wx + 44, 936, WINDOW)
        canvas.rect_outline(wx, 896, wx + 44, 936, HOUSE_DARK, 2)
        canvas.line(wx + 22, 896, wx + 22, 936, HOUSE_DARK, 2)
        canvas.line(wx, 916, wx + 44, 916, HOUSE_DARK, 2)
    # Tomato plant and flowers by the path.
    canvas.fill_circle(352, 946, 14, GREEN)
    canvas.fill_circle(348, 932, 6, ROOF)
    canvas.fill_circle(360, 936, 6, ROOF)
    canvas.fill_circle(672, 946, 14, GREEN)
    canvas.fill_circle(668, 932, 6, SUN)
    canvas.fill_circle(680, 936, 6, SUN)


def build_image():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)
    # Paper shading and double border.
    canvas.fill_rect(0, 0, WIDTH - 1, 18, PAPER_DARK)
    canvas.rect_outline(26, 26, WIDTH - 27, HEIGHT - 27, TEAL, 4)
    canvas.rect_outline(40, 40, WIDTH - 41, HEIGHT - 41, TEAL_LIGHT, 2)

    title_font = FONTS["title"]
    body_font = FONTS["body"]
    margin = 92
    max_w = WIDTH - 2 * margin

    draw_text(canvas, margin, 138, TITLE, title_font, TEAL, tracking=3)
    canvas.line(margin, 168, WIDTH - margin, 168, TEAL_LIGHT, 2)

    y = 210
    line_h = 36
    for para in PARAGRAPHS:
        for line in wrap(para, body_font, max_w):
            draw_text(canvas, margin, y, line, body_font, INK, tracking=2)
            y += line_h
        y += 14
    y += 6
    for line in SIGN_OFF:
        draw_text(canvas, margin, y, line, body_font, INK, tracking=2)
        y += line_h
    y += 10
    for line in wrap(POSTSCRIPT, body_font, max_w):
        draw_text(canvas, margin, y, line, body_font, INK, tracking=2)
        y += line_h
    return canvas, y


def main():
    canvas, text_end_y = build_image()
    draw_house_scene(canvas)
    png = canvas.to_png_bytes()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Clear the output dir's CONTENTS only; never remove the dir itself.
    for name in os.listdir(OUTPUT_DIR):
        path = os.path.join(OUTPUT_DIR, name)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            import shutil
            shutil.rmtree(path)

    with open(OUTPUT_PATH, "wb") as f:
        f.write(png)
    # Gate self-check: whole PNG, 1024x1024, at most 1 MiB. Fail loudly
    # rather than shipping an entry the scorer would refuse.
    with open(OUTPUT_PATH, "rb") as f:
        head = f.read(33)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    w, h = struct.unpack(">II", head[16:24])
    assert (w, h) == (WIDTH, HEIGHT), f"bad dimensions {w}x{h}"
    assert len(png) <= 1048576, f"PNG too big: {len(png)} bytes"
    assert text_end_y < 800, f"text runs into the house scene: {text_end_y}"
    print(f"wrote {OUTPUT_PATH}: {len(png)} bytes, "
          f"{WIDTH}x{HEIGHT}, text ends at y={text_end_y}")


if __name__ == "__main__":
    main()
