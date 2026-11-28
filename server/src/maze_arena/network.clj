(ns maze-arena.network
  (:require [clojure.java.io :as io])
  (:import [java.net ServerSocket]
           [java.io IOException]))

(defn handle-client [client]
  (let [address (.getRemoteSocketAddress client)]
    (println "Client connected:" address)
    (try
      (with-open [socket client
                  reader (io/reader socket :encoding "UTF-8")
                  writer (io/writer socket :encoding "UTF-8")]
        (loop []
          (when-let [line (.readLine reader)]
            (println address ":" line)
            (.write writer (str "Получено: " line "\n"))
            (.flush writer)
            (recur))))
      (catch IOException e
        (println "Connection error:" (.getMessage e)))
      (finally
        (println "Client disconnected:" address)))))

(defn start-server [port]
  (with-open [server (ServerSocket. port)]
    (println "Server listening on port" port)
    (while true
      (let [client (.accept server)]
        (future (handle-client client))))))
