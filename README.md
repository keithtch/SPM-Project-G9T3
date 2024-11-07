# SPM-Project-G9T3
 SMU IS212 Scrum Project - G9T3 - AY24-25 T1

## Developers
#    - Abigail, Keith, Jing Hang, Ren Yi, Wesley, Ziming

-> All testing has been automated into the CI/CD pipeline on Github
-> U may find the cypress test cases under 'cypress'/'e2e'

## NO NEED TO RUN THE CODE LOCALLY as everything has been deployed fully, can run it directly
-> https://booch.netlify.app/

## Login
1. Start WAMP, then start from login.html
2. All logins are via Staff ID
   HR Personnel Sample ID: 160008 (Sally Loh)
   Senior Management Sample ID: 130002 (Jack Sim)
   Manager Sample ID: 140103 (Sophia Toh) - Sophia is a subordinate of Jack 
   Staff Sample ID: 140893 (Bui Nyugen) - Bui is a subordinate of Sophia


## E2E Testing via Cypress
1. Visit https://nodejs.org/en
2. Download Node.js (LTS) make sure it's under PATH
3. Restart VSC
4. Can run command 'npm install cypress --save-dev'
5. Create test cases under cypress/e2e/1-getting-started
6. In one terminal run the command "python -m http.server 8000"
7. In another terminal, run the command 'npx cypress run' to generate test

## PyTest
1. Run "pip install -r requirements.txt"
2. Run 'cd api'
3. Run 'pytest test_application.py'

## Jest
1. Run 'npm run test'

## CI Pipeline Script
1. Inside .github/workflows/deploy.yml
