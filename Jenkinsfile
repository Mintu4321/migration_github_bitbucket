@Library('my-shared-library') _

pipeline {
    agent any

    stages {
        stage('Mirror Repos') {
            steps {
                mirrorGitHub('github_to_bit_bucket/main.py')
            }
        }
    }
}
