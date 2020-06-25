import os
from caller import call
from var_func import vf

"""
parser of the file:
TODO:
[] finish variable parser
  [X] need to implement var into var => actual: only one level of var work need n level of var work
  [] implement python function var
  [] finish implement path var

[] future
  [] implement db var
  [] make a compiler for simplified writting command
    [] autorisation token
    [] hash secure
    [] db for persistent store of the token
  [] make a secure credentials storage
"""


def load_file(filename): #the function for loading the file and init the line by line read
    with open('{}.lmcommand'.format(filename), 'r') as f:
        lines = f.readlines()

    return lines

def separate_headers(l): #separate the header of the content in compiled file
    print(l)
    i = l.index('----\n')
    header = l[:i]
    content = l[i+1:]
    return header, content

def header_check(header): # TODO: implement file hash verification and token verify
    token = header[0].split(':')[1].strip()
    filehash = header[1].split(':')[1].strip()
    return token, filehash

def command_traitement(content): #this is the core func where we call the var checker, call the func into subprocess and check the result
    vars = {}
    print(content)
    for command in content:
        command = command.rstrip()
        command = check_command_variables(command, vars)
        print(f"command for call is {command}")
        res = call(command)
        if res.returncode !=0:
            print(f"erreur: {res.stderr}")

def check_command_variables(command, vars, sub=False): #this function check if a variable is in the line and call the var execute function for render command
    print(f"command is {command}")
    if not '{%' in command: # si aucun snippet/variable n'est dans la ligne, on rend juste la ligne splitted
        print('any command in this line')
        return command.split(' ')
    else:
        splitted = command.split(' ') #sinon on commence par splitter la ligne
        for id, c in enumerate(splitted): #our enumerer les items
            print(id, c)
            if not '{%' in c: #si le debut du snippet/variable n'est pas dans le mot on passe au suivant
                continue
            else: 
                content = c[c.find('{%')+2:c.rfind('%}')] #on slice la string avec comme borne la première ouverture de snippet et la dernière fermeture du mot passer en paramètres
                vtype, value = separate_variables(content) #on sépare le type du contenu
                if '{%' in value:
                    value, vars = check_command_variables(content, vars, sub=True) #si un snippet est contenue dans le contenu (/!\ impossible de le mettre en type (1: inutile 2: ne sert à rien)) et
                value, vars = variable_execute(vtype, value, vars) #on dit que c'est un sous appel -> recursion pour traiter tout les snippet/variables + on execute le snippet/variable
                print(f'value is {value}')
                if sub: #si c un sous programme on récupère juste la sortie de l'execution du sous snippet/variables avec le dictionnaire des variables
                    return value, vars
                else:
                    splitted[id] = value #sinon si c'est le première appel, on formatte la ligne de mot avec le resultat
                    return splitted
"""

 => on traite les variables/snippets par cascade

"""


def separate_variables(content):
    typev, value = content.split(':', 1) # on sépare le type et la valeur avec uniquement le premier split de ":" => evite de splitter des sous snippet/variables
    typev = typev.split('_') #on traite les les types du snippet
    return typev, value


def variable_execute(typev, value, vars): #this function execute variable snippet and replace it for make valid commandline command
    for vartype in typev:
        print(f"variables type: {vartype} value: {value}")
        try:
            value = vf.run_func(vartype, params=[value, vars])
        except NotImplementedError:
            print(f"not implemented for {vartype}")

            if vartype.split('=')[0] == 'v':
                varname = vartype.split('=')[1]
                if varname in vars:
                    value = vars[varname]
                    print(f"acces to var: {varname} -> {value}")
                else:
                    raise ValueError
            
            elif vartype.split('=')[0] == 's':
                varname = vartype.split('=')[1]
                if varname not in vars:
                    vars[varname] = value
                    print(f"set to var: {varname} -> {value}")

            else:
                raise ValueError("unknown variable type %s" % vartype)

    return value, vars


l = load_file('test')
header, content = separate_headers(l)
creditential = header_check(header)
command_traitement(content)

print(creditential)
