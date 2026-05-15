import org.apache.tools.ant.taskdefs.condition.Os

plugins {
    id("org.openapi.generator") version "7.19.0"
}

group = "ru.vl"

repositories {
    mavenCentral()
}

val pypiToken = project.findProperty("pypi.token")?.toString()
    ?: System.getenv("POETRY_PYPI_TOKEN_PYPI")
    ?: System.getenv("PYPI_PASSWORD")
    ?: ""

val clientFolderPath = (findProperty("CLIENT_FOLDER_PATH") ?: "") as String
val outputDir = layout.projectDirectory.dir("api-docs").asFile
val openapiFileName = (findProperty("OPENAPI_SPEC_FILE_NAME") ?: "") as String
val outputFile = File(outputDir, openapiFileName)

tasks.register<Exec>("fetchSwagger") {
    group = "evawiki"
    doFirst {
        if (!outputDir.exists()) outputDir.mkdirs()
    }

    commandLine(
        "curl", "https://docs.evateam.ru/files/obj/CmfDocument/CmfDocument:d22/CmfDocument:d22c35d4-581b-11f0-bfd0-00161e12a413/oas_evateam_v1_9_22.json",
        "-H", "accept: application/json,*/*",
        "-o", outputFile.absolutePath
    )
}

tasks.register<Exec>("processSwagger") {
    group = "evawiki"
    dependsOn("fetchSwagger")

    commandLine("python3", "scripts/process_swagger.py", outputFile.absolutePath)
}

openApiGenerate {
    generatorName = "python"
    skipValidateSpec.set(true)
    generateApiDocumentation.set(false)
    generateModelDocumentation.set(false)
    generateApiTests.set(false)
    generateModelTests.set(false)
    inputSpec.set("$rootDir/api-docs/$openapiFileName")
    outputDir.set("$rootDir/$clientFolderPath")
    templateDir.set("$rootDir/src/main/resources/openapi-templates")
    configOptions.set(mapOf(
        "packageName" to "evawiki_client",
        "projectName" to "evawiki-python-client",
        "packageVersion" to "0.1.9"
    ))
    gitHost.set("github.com")
    gitUserId.set("vanleo85")
    gitRepoId.set("evawiki-python-client")

}

tasks.named("openApiGenerate") {
    dependsOn("processSwagger")
}

tasks.register<Exec>("installPoetryIfNeeded") {
    group = "evawiki"
    description = "Installs poetry if not present"

    // Проверяем, установлен ли poetry, и если нет - устанавливаем
    commandLine("sh", "-c", "command -v poetry >/dev/null 2>&1 || pip install poetry")
}

tasks.register<Exec>("buildClient") {
    group = "evawiki"
    description = "Builds the generated python client using poetry"
    dependsOn("openApiGenerate", "installPoetryIfNeeded")

    workingDir = layout.projectDirectory.dir(clientFolderPath).asFile
    commandLine("sh", "-c", "poetry build")
}

// Задача для настройки учетных данных Poetry (выполняется один раз вручную)
tasks.register<Exec>("setupPoetryCredentials") {
    group = "evawiki"
    description = "Sets up Poetry credentials for PyPI publishing (run manually once)"

    workingDir = layout.projectDirectory.dir(clientFolderPath).asFile

    onlyIf {
        if (pypiToken.isEmpty()) {
            println("Warning: PyPI token not found. Skipping credentials setup.")
            false
        } else true
    }

    if (pypiToken.isNotEmpty()) {
        if (Os.isFamily(Os.FAMILY_WINDOWS)) {
            commandLine("cmd", "/c", "poetry", "config", "pypi-token.pypi", pypiToken)
        } else {
            commandLine("sh", "-c", "poetry config pypi-token.pypi  $pypiToken")
        }
    }
}

// Вспомогательная задача для публикации
tasks.register<Exec>("actualPublishToPyPI") {
    group = "evawiki"
    description = "Actual publishing task that runs only when credentials are available"

    dependsOn("buildClient", "setupPoetryCredentials")
    workingDir = layout.projectDirectory.dir(clientFolderPath).asFile

    onlyIf { pypiToken.isNotEmpty() }

    commandLine("sh", "-c", "poetry publish")
}

// Основная задача публикации
tasks.register("publishToPyPI") {
    group = "evawiki"
    description = "Publishes the built python client to PyPI"
    dependsOn("actualPublishToPyPI")

    doFirst {
        if (pypiToken.isEmpty()) {
            throw GradleException("Cannot publish to PyPI: token is missing. Set 'pypi.token' property or POETRY_PYPI_TOKEN_PYPI env var.")
        }
    }
}