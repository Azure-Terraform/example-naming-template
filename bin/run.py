#!/usr/bin/python

import requests
from requests.exceptions import HTTPError

import yaml
import json
import os.path

from mdutils import MdUtils

def importEntity(url, entity_json):
    # Fetch information from M$oft and parse
    contents = webScrape(url)
    entities = parseMarkdown(contents)
    
    # Open local data and merge
    if os.path.isfile(entity_json): 
        local_entities = json.load(open(entity_json,))
        #local_entities = yaml.load(
        #                    open(entity_yaml),
        #                    Loader=yaml.FullLoader)

        combined_entities = {**entities,**local_entities}
        entities = combined_entities
    
    # Write output data
    with open(entity_json, 'w') as outfile:
        json.dump(entities,
                outfile,
                sort_keys = False,
                indent=4)
    
    #yaml.dump(entities, 
    #          open(entity_yaml, 'w'),
    #          indent=4, 
    #          sort_keys=False,
    #          default_flow_style=False)

    return entities

def parseMarkdown(content):

    entities = dict()

    # Split markdown into sections based on header tag
    sections = content.decode('utf8').strip('\n').split('## ')
    
    for section in sections:
        
        lines = section.split('\n')
        
        # Split section into lines based on crlf
        for line in lines:
            
            if line.startswith('Microsoft.'): 
                
                category = line[10:]
            
            elif line.startswith('> |'):
                
                # This is a row that contains a naming rule
                fields = line.split('|')
                
                if ((fields[1].strip(' ') != 'Entity') and 
                    (fields[1].strip(' ') != '---')):
                    
                    #Extract data
                    path = fields[1].strip(' ').replace(" ", "")
                    entity = path.split("/")[-1]
                    scope = fields[2].strip(' ')
                    length = fields[3].strip(' ')
                    maxlength = length.split("-")[-1]
                    rules = fields[4].strip(' ').lower()

                    # Normalize data
                    if (("63 characters" in maxlength) or
                        (maxlength == '')): 
                        
                        maxlength = "63"
                    elif("98" in maxlength): 
                        maxlength = "98"
                    elif("64" in maxlength):
                        maxlength = "64"
                    elif("bit integer" in maxlength):
                        maxlength = "64"
                    elif("resource name" in maxlength):
                        maxlength = "255"

                    if (("hyphen" in rules) or
                        ("%" in rules) or
                        ("[]" in rules) or
                        ("&" in rules) or
                        ("any url" in rules) or
                        ("all characters" in rules)): 
                        
                        rules = "a-9"
                    
                    elif (("letters and numbers" in rules) or
                        ("letters or numbers" in rules) or
                        ("alphanumerics" in rules)): 
                        
                        rules = "a9"

                    elif("default" in rules):
                        rules = "default"

                    elif("numbers and periods" in rules):
                        rules = "0.9"

                    # Add to dictionary
                    if path not in entities.keys(): entities[path] = list()
                    
                    entities[path].append({
                            'category' : category,
                            'entity' : entity,
                            'scope' : scope,
                            'maxlength': maxlength,
                            'rule': rules,
                            'convention': '',
                            'example': ''
                        })
                    
    return entities
            
def webScrape(url):
    # Go fetch the markdown from the web
    try:
        response = requests.get(url)

        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.8
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.8
    else:
        #  Request was successful
        return response.content

def importCustom(custom_json):
    if os.path.isfile(custom_json): 
        
        #custom_entities = yaml.load(
        #                    open(custom_yaml),
        #                    Loader=yaml.FullLoader)
        
        custom_entities = json.load(open(custom_json,))
        
        
        for e in custom_entities.values():
            
            maxlength = e.get('maxlength')
            rule = e.get('rule')
            allowed_values = e.get('allowed_values')
            # Loop through the list of allowed values and check
            for key in allowed_values.keys():
                # Blow up if user entered value greater than the allowed length.
                if len(key) > int(maxlength): 
                    raise ValueError("Length of "+key+" exceeds maximum value of "
                                    +maxlength+" set for this entity.")
                
                # And if they say lowercase and alphanumeric and it isnt
                if ((rule == 'az') 
                    and (
                        not key.islower() 
                        or not key.isalnum()
                        )):
                    raise ValueError("You have specified convention is "+
                                    rule+" but your allowed value contains "+
                                    key)
                    
                    # If they just specify lower
                if (rule == 'a-z') and not key.islower():
                    raise ValueError("You have specified convention is "+
                                    rule+" but your allowed value contains "+
                                    key)
                    

        return custom_entities

def exportMarkdown(title,custom,entities):
    ### BEGIN REMOVE THIS SECTION BEFORE GENERAL USE ###   
    mdf.new_header(level=1, title='DO NOT USE THIS REPOSITORY IN PRODUCTION')
    mdf.new_paragraph(
        "It is used in example code within the Azure-Terraform module codebase. "
    )
    mdf.new_line(
        "* This repository can be used as a template to create a private repository "
        "which would contain proprietary data within the custom.json file "
        "reflective of the organization in which it was to be used. "
    )
    ### END REMOVE THIS SECTION BEFORE GENERAL USE ###   
    mdf = MdUtils(file_name='README',title=title)


    # Create the Overview Section
    mdf.new_header(level=1, title='Overview')
    mdf.new_paragraph(
        "This repository contains a list of variables and standards for naming "
        "resources in Microsoft Azure.  It serves these primary purposes:"
    )
    mdf.new_line(
        "* A central location for development teams to research and collaborate "
        "on allowed values and naming conventions."
    )
    mdf.new_line(
        "* A single source of truth for data values used in policy "
        "enforcement, billing, and naming."
    )
    mdf.new_line(
        "* A RESTful data source for application requiring information on approved "
        "values, variables and names."
    )
    mdf.new_header(level=2, title='How to Use')
    mdf.new_paragraph(
        "This repository has four primary areas and their methods of use are described "
        "by the following:"
    )
    mdf.new_line(
        "* **README.md** - The readme is the human readable documentation on the naming "
        "conventions, approved values, and variable names that developers will reference "
        "when creating inputs for modules and code."
    )
    mdf.new_line(
        "* **custom.json** - Data in json format to be RESTful sourced by "
        "applications. Contains a list of custom variable names, conventions, scope and approved "
        "values.  The readme is generated automatically from this data."
    )
    mdf.new_line(
        "* **entity.json** - Data in json format to be sourced by "
        "applications. Contains an up-to-date list of Azure resources, conventions, scope and approved "
        "naming conventions.  The readme is generated automatically from this data."
    )
    mdf.new_line(
        "* **bin/run.py** - A python script that scrapes the latest data from Microsoft merges "
        "with the existing json and adds new resources.  It also generates this README doc "
        "from the custom and entity json."
    )
    mdf.new_header(level=2, title='How to Update')
    mdf.new_paragraph(
        "This information is meant to be a living source of truth for applications and "
        "policy and as such is expected to be versioned and updated.  If you wish to add "
        "allowed values for any of the variables or need a naming convention that is not "
        "provided in this data, open an issue request agains this repo. Upon review the "
        "information will be updated and the policy engines will reflect the changes "
        "immediately."
    )

    # Create the Custom Entity Section
    mdf.new_header(level=1, title='Custom Entities')
    mdf.new_paragraph(
        "Custom entities are "
        "variables and allowed values that describe our business and purpose "
        "at the company and are the only approved values to be used in names and tags. "
        "This assures consistency and data integrity across all resources being "
        "named and tagged in Azure.  If you would like to add additional allowed "
        "values, simply open an issue request against this repo and upon review "
        "the value will be added. "
    )

    # Role through the custom dictionary
    for name,e in sorted(custom.items()):
        mdf.new_header(level=2, title='custom.'+name)
        
        entity_tbl = [
            '<sub>Full Text</sub>',
            '<sub>Scope</sub>',
            '<sub>Rule</sub>',
            '<sub>Value</sub>'
        ]
        
        entity_dict = e.get('allowed_values')
        entity_count = len(entity_dict)+1
        
        scope = e.get('scope')
        rule = e.get('rule')+'['+e.get('maxlength')+']'
        
        for key,value in entity_dict.items():
            long_name = value
            variable = key
            entity_tbl.extend([
                '<sub>' + long_name + '</sub>',
                '<sub>' + scope + '</sub>',
                '<sub>' + rule + '</sub>',
                '<sub>' + variable + '</sub>'
            ])

        mdf.new_table(columns=4,rows=entity_count,text=entity_tbl,text_align='center')

    # Create the Azure Entity Section
    mdf.new_header(level=1, title='Azure Entities')
    mdf.new_paragraph(
        "Azure entities are entities as maintained by Microsoft Azure and should "
        "contain all possible resources that can be built along with Microsoft's "
        "rules for record length, scope, and allowed characters.  Naming convention "
        "is specific to the company and takes into account the scope, length, and purpose "
        "to assure the name retains readability and conveys the most pertinent "
        "information about the resource to the reader.  Examples are provided. "
    )

    category_lst = {}
    for entity in entities:
        for e in entities[entity]:
            category = e['category']
            
            if category not in category_lst.keys(): category_lst[category] = []
            
            category_lst[category].append(entity)
    
    for category in sorted(category_lst):
        mdf.new_header(level=2, title='azure.'+category)

        entity_count = len(category_lst[category]) + 1
        entity_tbl = [
            '<sub>Entity</sub>',
            '<sub>Scope</sub>',
            '<sub>Rule</sub>',
            '<sub>Convention</sub>',
            '<sub>Example</sub>'
        ]

        for entity in sorted(category_lst[category]):

            for e in entities[entity]:
                category_name = e['category']
                if category_name == category:
                    entity_name = e['entity']
                    scope = e['scope']
                    rule = e['rule']+'['+e['maxlength']+']'
                    convention = e['convention']
                    example = e['example']
            
                    entity_tbl.extend([
                        '<sub>' + entity_name + '</sub>',
                        '<sub>' + scope + '</sub>',
                        '<sub>' + rule + '</sub>',
                        '<sub>' + convention + '</sub>',
                        '<sub>' + example + '</sub>'
                    ])
            
        mdf.new_table(columns=5,rows=entity_count,text=entity_tbl,text_align='center')


    # Write the markdown file
    mdf.create_md_file()  

def createLinks(custom,entities):
    with open('README.md', 'r') as file:
       filedata = file.read()
    
    # Handle the gitlab table thing
    filedata = filedata.replace(':---:','------')

    # Go through the custom entities and create links
    for name,e in custom.items():
        maxlength = e.get('maxlength')
        filedata = filedata.replace('<custom.'+name,'<[custom.'+name+'['+maxlength+']](README.md#custom'+name+')')

    with open('README.md', 'w') as file:
        file.write(filedata) 

def main():
    url = ('https://raw.githubusercontent.com/MicrosoftDocs/'+
            'azure-docs/master/articles/azure-resource-manager/'+
            'management/resource-name-rules.md')
    #entity_yaml = "entity.yaml"
    #custom_yaml = 'custom.yaml'
    custom_json = 'custom.json'
    entity_json = "entity.json"

    #entities = importEntity(url,entity_yaml)
    entities = importEntity(url,entity_json)
    #custom = importCustom(custom_yaml)
    custom = importCustom(custom_json)

    #with open('output/entity.json', 'w') as outfile:
    #    json.dump(entities, outfile, indent=4)

    #with open('output/custom.json', 'w') as outfile:
    #    json.dump(custom, outfile, indent=4)

    exportMarkdown('Custom Naming Conventions for Azure',custom,entities)
    createLinks(custom,entities)

if __name__ == '__main__':
    main()
