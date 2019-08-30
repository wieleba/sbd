import os
from shutil import copyfile

class HtmlPrinter:

    def __init__(self, out_dir, out_file_name):
        self.out_dir = out_dir
        self.out_file_name = out_file_name


    def preable(self):
        copyfile('style.css',self.out_dir + '/style.css')
        copyfile('style2.css',self.out_dir + '/style2.css')

        try:
           a = open(os.path.join(self.out_dir,out_file_name + '.html'),'w')
           a.write(
                   '''<html>
                            <head>
                               <meta charset="utf-8"/>
                               <link rel="stylesheet" href="style.css" /> 
                               <link rel="stylesheet" href="style2.css" />
                            </head>
                            <body>''')
           self.out = a
           return a
        except IOError:
            print ('Can\'t open ',out_file_name)
            exit(1)

    def write_content(self, content):
        self.out.write('\n')
        if(content is not None):
            self.out.write('<div class="page">')
            self.out.write(re.sub(r'href=".*\.xhtml',r'href="'+ self.out_file_name + '.html', content.replace('src="/','src="./')))
            self.out.write('</div>')

    def finalize(self):
        self.out.write('</body></html>')
        self.out.close()
