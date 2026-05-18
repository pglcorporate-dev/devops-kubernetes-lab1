resource "kubernetes_service" "magic" {

  metadata {
    name = "magic-number"
  }

  spec {

    selector = {
      app = "magic"
    }

    port {

      port        = 5000
      target_port = 5000
    }

    type = "NodePort"
  }
}