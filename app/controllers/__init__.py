"""
User opens browser ----> Visits "/" ----> welcome() ----> MainController().render({'files_valid': None}) ----> Renders "welcome.html"
       |
       | (User fills form and submits)
       v
Submits to "/validate" ----> upload_and_validate() ----> MainController().validate_files()
       |
       |---> Validation Fails ----> self.render({'files_valid': False}) ----> Renders "welcome.html" with error
       |
       `---> Validation Succeeds ----> self.render({'files_valid': True}) ----> Renders "welcome.html" with success

"""
