import groovy.json.JsonSlurperClassic

def call(String scriptName) {
    withCredentials([string(credentialsId: 'bitbucket-github-json', variable: 'CRED_JSON')]) {
        def creds

        try {

            creds = new JsonSlurperClassic().parseText(env.CRED_JSON)

        } catch (Exception e) {

            error "❌ Failed to parse credentials JSON: ${e.message}"

        }

        def envVars = [
            "BITBUCKET_USERNAME=${creds.BITBUCKET_USERNAME}",
            "PASSWORD=${creds.BITBUCKET_APP_PASSWORD}",
            "BITBUCKET_WORKSPACE=${creds.BITBUCKET_WORKSPACE}",
            "GITHUB_USER=${creds.GITHUB_USER}",
            "GITHUB_TOKEN=${creds.GITHUB_TOKEN}"
        ]

        echo "📢 Executing Python script: ${scriptName}"
        echo "🔐 Using user: ${creds.BITBUCKET_USERNAME} and GitHub: ${creds.GITHUB_USER}"

        withEnv(envVars) {
            sh """
            python3 -m pip install --upgrade pip
            python3 -m venv venv
            source venv/bin/activate
            pip3 install -r requirements.txt
            python3 ${scriptName}
            """
        }
    }
}

