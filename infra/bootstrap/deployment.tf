resource "kubernetes_deployment" "magic" {

  metadata {
    name = "magic-number"
  }

  spec {

    replicas = 1

    selector {
      match_labels = {
        app = "magic"
      }
    }

    template {

      metadata {
        labels = {
          app = "magic"
        }
      }

      spec {

        container {

          name  = "magic"
          image = "magic-number:1.0"

          image_pull_policy = "Never"

          port {
            container_port = 5000
          }
        }
      }
    }
  }
}