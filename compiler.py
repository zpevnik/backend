#!/usr/bin/python

with open('test.txt', 'r') as file:
   content = file.readlines()

class translator(object):

   def translate_to_tex(self, song):

      def finish_part():
         if self.state_chorus:
            self.state_chorus = False
            output += "\\endchorus"
         elif self.state_verse:
            self.state_verse = False
            output += "\\endverse"

      self.state_chorus = False
      self.state_verse = False   
      output = ""

      for line in song:
         if line == "#####":
            finish_part()
            self.state_verse = True
            output += "\\beginverse"

         elif line == "*****":
            finish_part()
            self.state_chorus = True
            output += "\\beginchorus"

         elif line == "******":
            finish_part()
            output += "\\repchoruses"
         else:
            line = line.replace('>', '\echo{')
            line = line.replace('<', '}')

            line = line.replace('||{', '\\rrep\\rep{')
            line = line.replace('||', '\\rrep')
            line = line.replace('|', '\\lrep')

            output += line

      print output

content = [x.strip() for x in content]

x = translator()
x.translate_to_tex(content)


#state_chorus = False
#state_verse = False
#
#content = [x.strip() for x in content]
#for line in content:
#
#   if line == "#####":
#      if state_chorus:
#         print "\\endchorus"
#         state_chorus = False
#      elif state_verse:
#         print "\\endverse"
#         state_verse = False
#      print "\\beginverse"
#      state_verse = True
#   elif line == "*****":
#      if state_chorus:
#         print "\\endchorus"
#         state_chorus = False
#      elif state_verse:
#         print "\\endverse"
#         state_verse = False
#      print "\\beginchorus"
#      state_chorus = True
#   elif line == "******":
#      if state_chorus:
#         print "\\endchorus"
#         state_chorus = False
#      elif state_verse:
#         print "\\endverse"
#         state_verse = False
#      print "\\repchoruses"
#   else:
#      line = line.replace('>', '\echo{')
#      line = line.replace('<', '}')
#
#      line = line.replace('||{', '\\rrep\\rep{')
#      line = line.replace('||', '\\rrep')
#      line = line.replace('|', '\\lrep')
#      print line
