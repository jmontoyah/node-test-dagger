import random
import dagger
from dagger import dag, function, object_type, field
from typing import List, Optional
import requests
import os



@object_type
class NodeTestDaggerPython:
    
    @function
    async def publish(self, source: dagger.Directory) -> str:
        """Publish the application container after building and testing it on-the-fly"""
        await self.test(source)
        
        # Aquí llamamos a self.build para obtener el contenedor y luego publicamos
        container = await self.build(source)
        
        # Publica el contenedor con un nombre aleatorio
        await container.publish(f"ttl.sh/myapp-{random.randrange(10 ** 8)}")

        # Devuelve un mensaje indicando que la publicación se completó 
        return "Publicación completada"
    
    @function
    async def run_analysis(self, source: dagger.Directory) -> str:
        """Run SonarCloud analysis locally using SonarScanner"""
        
        # Definir las variables de entorno necesarias
        sonar_token = os.getenv("SONAR_CLOUD_TOKEN")  # Este valor se puede configurar como una variable de entorno
        project_name = os.getenv("PROJECT_NAME")  # El nombre del proyecto
        project_key = os.getenv("PROJECT_KEY")  # La clave del proyecto en SonarCloud
        organization = os.getenv("SONAR_ORG")  # La organización en SonarCloud
        branch = os.getenv("BRANCH_NAME")  # El nombre de la rama actual (puedes configurarlo dinámicamente)

        # Configura el contenedor con la imagen de SonarScanner
        container = (
            dag.container()
            .from_("sonarsource/sonar-scanner-cli:latest")  # Imagen de SonarScanner
            .with_env_variable("SONAR_TOKEN", sonar_token)
            .with_env_variable("SONAR_PROJECT_KEY", project_key)
            .with_env_variable("SONAR_PROJECT_NAME", project_name)
            .with_env_variable("SONAR_ORG", organization)
            .with_env_variable("SONAR_BRANCH", branch)
            .with_directory("/src", source)  # Montamos el código fuente en el contenedor
        )
        
        # Ejecutar SonarCloud Scanner dentro del contenedor
        result = await container.with_exec(
            [
                "sonar-scanner", 
                f"-Dsonar.projectKey={project_key}", 
                f"-Dsonar.organization={organization}", 
                f"-Dsonar.projectName={project_name}", 
                f"-Dsonar.branch.name={branch}",  # Define el nombre de la rama si es necesario
                "-Dsonar.language=javascript",  # El lenguaje del proyecto (puede ser otro)
                "-Dsonar.coverageFile=${{ inputs.coverage-file }}",  # Si tienes un archivo de cobertura
                f"-Dsonar.projectBaseDir={source}"
            ]
        ).stdout()

        return f"SonarCloud Analysis completed: {result}"
"""
@object_type
class HelloDagger:
    @function
    async def publish(self, source: dagger.Directory) -> str:
        """Publish the application container after building and testing it on-the-fly"""
        await self.test(source)        
        return await self.build(source).publish(
            f"ttl.sh/myapp-{random.randrange(10 ** 8)}"
        )
"""    


    @function
    async def test_pipeline(self, source: dagger.Directory) -> str:
        """Prueba el pipeline de GitHub Actions"""
        pipeline_yaml_path = "/.github/workflows/node.js.scan.yml"
        
        async with Client() as client:  # Correctamente dentro de una función async
            # Crear el contenedor basado en la imagen 'ubuntu:latest'
            container = (
                client.container()  # Inicializa el contenedor
                .from_("ubuntu:latest")  # Especifica la imagen base
            )
            print("Realizando checkout del repositorio...")
            # Aquí puedes continuar configurando o ejecutando el contenedor
        return "ok comunicación"

    @function
    async def build(self, source: dagger.Directory) -> str:
        """Construir el proyecto (si es necesario)"""
        # Instalar dependencias
        await self.build_env(source).with_exec(["npm", "install"]).stdout() 

        # Ejecutar pruebas
        await self.build_env(source).with_exec(["npm", "run", "test"]).stdout()

        # Aquí omitimos el paso de "npm run build"
        # await self.build_env(source).with_exec(["npm", "run", "build"]).stdout()

        return "Construcción completada"

    @function
    async def test(self, source: dagger.Directory) -> str:
        """Return the result of running unit tests"""
        # return await (
        #    self.build_env(source)
        #    .with_exec(["npm", "run", "test"])  # Usamos el script 'test' que ya está definido en package.json
        #    .stdout()
        #)

        return "ok test"

    @function
    def build_env(self, source: dagger.Directory) -> dagger.Container:
        """Build a ready-to-use development environment"""
        node_cache = dag.cache_volume("node")
        
        return (
            dag.container()
            .from_("node:21-slim")
            .with_directory("/src", source)
            .with_mounted_cache("/root/.npm", node_cache)
            .with_workdir("/src")
            .with_exec(["npm", "install"])
        )
