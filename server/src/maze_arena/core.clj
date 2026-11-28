(ns maze-arena.core
  (:require [maze-arena.network :as network]))

(defn -main []
  (network/start-server 5000))
