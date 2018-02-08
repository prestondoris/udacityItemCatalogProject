# Brewery Catalog

**Create, Read, Update, and Delete items in a catalog**

An application that provides a list of beers within a variety of breweries as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## To Use
To run and view this app you'll need:
1. Install Vagrant and Virtual Box
2. Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repo
3. Clone the [udacityItemCatalogProject](https://github.com/prestondoris/udacityItemCatalogProject) repo into the vagrant directory
4. Run the following command line prompts

```
# Launch the vagrant vm
vagrant up
# Connect to the VM
vagrant ssh
# Change to the projectItemCatalog directory in the VM
cd /vagrant/udacityItemCatalogProject
# Run the server
python itemCatalog.py
```

### Notes
The populateDB.py file is used to RESET the DB to the original entries with no users. This file should NOT be run unless a serious issue occurs.

### Bugs
There is a known bug when Preston Doris (the creator of this app) logs into the app via Google. The Google is unable to revoke the token. This issue resolves itself when the token expires. It is unknown what is actually causing this issue to happen. This has not happened with other users.
