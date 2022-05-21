package com.mycompany.http;

import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 *
 * @author pacos
 */
public class threadPool implements Runnable{
    
    private final int port;
    protected ServerSocket serverSocket = null;
    protected Thread runningThread= null;
    protected final ExecutorService pool = Executors.newFixedThreadPool(5);

    public threadPool(int port) {
        this.port = port;
    }

    @Override
    public void run() {
        Socket client;
        synchronized(this){
            this.runningThread = Thread.currentThread();
        }
        try {
            serverSocket = new ServerSocket(port);
        } catch(Exception ex) {
            throw new RuntimeException("Cannot init socket at port: " +
                    serverSocket.getLocalPort(), ex);
        }
        for(;;){
            try {
                client = serverSocket.accept();
            } catch (Exception ex) {
                throw new RuntimeException("Error accepting connection", ex);
            }
            pool.execute(new webServer(client));
        }
    }
    
    public static void main(String args[]) {
        threadPool pool = new threadPool(8000);
        new Thread(pool).start();
    }
    
}