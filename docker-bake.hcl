# Aufruf:   docker buildx bake [trixie|alpine|hardened]

# Dateiformate: HCL ( = HashiCorp Configuration Language), YAML (wie in Docker Compose) oder JSON
# HCL ist maechtiger und flexibler als YAML oder JSON.

# https://docs.docker.com/build/bake/introduction
# https://docs.docker.com/build/bake/reference

group "default" {
    targets = ["trixie", "alpine"]
    # targets = ["hardened", "trixie", "alpine"]
}

# Benoetigt eine Docker-Business-Subscription mit Zugriff auf dhi.io (Docker Hardened Images)
target "hardened" {
    tags = ["gast:0.1.0-hardened"]
    #dockerfile = "Dockerfile"
    #no-cache = true
}

target "trixie" {
    tags = ["gast:0.1.0-trixie"]
    dockerfile = "Dockerfile.trixie"
    #no-cache = true
}

target "alpine" {
    tags = ["gast:0.1.0-alpine"]
    dockerfile = "Dockerfile.alpine"
    #no-cache = true
}
