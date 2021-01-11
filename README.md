**Description:**
- This is django project which create rest APIs for user authentication and note creation.
- In this project contains Two Apps:
   1. __User__
   2. __Notes__ 

***1.User:***

- It contains RegisterAPI, LoginAPI, LogoutAPI, ForgotPasswordAPI, ResetPasswordAPI and UserProfileAPI.

- So in this User login registration app we firstly register user. 
     - For authentication , `JWT Token` used. 
     - After successfully registration user got one verification token on provided email. 
     - After clicking on that token user successfully activate token. and then do login. 
- I create separate APIs for forgotapssword, resetpassword and logout password. 
- In this user app, used `Signals` for adding profile image to respective userid.
---
***2.Note_App:***
- It Provide Following APIs for notes :
    - Create Note
    - Update Note
    - Archive Note
    - Pin Note
    - Trash Note
    - Restore Note (from trash)
    - Delete Note
    - Create Label
    - Update Label
    - Delete Label

- It contains CreateNote, UpdateNote, CreateLabel, Update Label apis.

- Here User can create notes and label.
