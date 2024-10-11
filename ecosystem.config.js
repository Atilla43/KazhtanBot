 module.exports = {
  apps: [{
   name: "kaztan_bot",
   script: "main.py",
   env: {
    "NODE_ENV": "development",
   },
   env_production: {
    "NODE_ENV": "production",
   }
  }]
 }