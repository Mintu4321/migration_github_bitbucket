import groovy.json.JsonSlurperClassic

def call(String scriptName) {
    withCredentials([string(credentialsId: 'bitbucket-github-json', variable: 'CRED_JSON')]) {
        def creds = new JsonSlurperClassic().parseText(env.CRED_JSON)

        def envVars = [
            "BITBUCKET_USERNAME=${creds.BITBUCKET_USERNAME}",
            "PASSWORD=${creds.BITBUCKET_APP_PASSWORD}",
            "BITBUCKET_WORKSPACE=${creds.BITBUCKET_WORKSPACE}",
            "GITHUB_USER=${creds.GITHUB_USER}"
        ]

        echo "📢 Executing Python script: ${scriptName}"
        echo "🔐 Using user: ${creds.BITBUCKET_USERNAME} and GitHub: ${creds.GITHUB_USER}"

        withEnv(envVars) {
            sh """
            python3 -m pip install --upgrade pip
            pip3 install -r requirements.txt
            python3 ${scriptName}
            """
        }
    }
}

