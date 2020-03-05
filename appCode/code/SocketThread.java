package com.bergerrob.robodog;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

public class SocketThread extends Thread {
    public enum Status{DISCONNECTED,CONNECTING,CONNECTED,ERROR_HOST,ERROR_IO}

    //info about the socket
    String host;
    int port;
    Socket socket;
    PrintWriter out;
    Status status=Status.DISCONNECTED;

    //lock for concurrency, so the main thread can call on this one when it needs to interact with the socket
    Object lock;

    //the message to send over, this way the main thread can access the instance's member
    String message;
    /*messages with a special value (not super duper implemented yet...
        disconnect: disconnects, obviously (app should ask before sending this off to the thread)
        reconnect: disconnects if it can, then reconnects, obviously
        check: checks connection
     */
    //String threadStatus="nothing yet";//dumb idea for relaying messages back to the main thread, not sure how else to go about it

    //really simple constructor
    public SocketThread(String h,int p){
        super();
        host=h;
        port=p;
    }

    public void disconnect(){
        status=Status.DISCONNECTED;
        if(out!=null){
            out.println("disconnect");//let the server know we're leaving
            out.close();
        }
        if(socket!=null){
            try{
                socket.close();
            }catch(IOException e){
                System.out.println("ERROR: IOException...");
                System.out.println("\t" + e.getMessage());
            }
        }
    }
    public void shutdown(){
        status=Status.DISCONNECTED;
        if(out!=null){
            out.println("playdead");//let the server know we're leaving
            out.close();
        }
        if(socket!=null){
            try{
                socket.close();
            }catch(IOException e){
                System.out.println("ERROR: IOException...");
                System.out.println("\t" + e.getMessage());
            }
        }
    }

    /*public boolean isConnected(){
        return socket.isConnected();
    }
    public String getThreadStatus(){
        return threadStatus;
    }
    public void updateStatus(){
        if(socket.isConnected()){
            status=Status.CONNECTED;
        }else{
            status=Status.DISCONNECTED;
        }
    }*/

    @Override
    public void run() {
        System.out.println("Trying to connect...");
        status=Status.CONNECTING;
        //threadStatus="tryin";
        if(lock==null) {//call because it just might need to call itself when it reconnects...
            lock = new Object();
        }

        try(//the actual connection
                Socket s = new Socket(host,port);
                PrintWriter o=new PrintWriter(s.getOutputStream(),true);
                //instream? If the server can send a message before it goes off or something?
        ){
            socket=s;
            out=o;
            if(!socket.isConnected()) {
                status=Status.DISCONNECTED;
                //threadStatus="NOT CONNECTED";
                System.out.println("NOT CONNECTED");
            }else{
                status=Status.CONNECTED;
                //threadStatus="CONNECTED";
                System.out.println("CONNECTED");
            }
            //out.println("CONNECTED");

            synchronized (lock) {//so the main thread can wake it up when needed
                while (true) {
                    try {
                        lock.wait();
                        switch(message){
                            case "disconnect":
                                System.out.println("disconnect message");
                                disconnect();
                                break;
                            case "playdead":
                                System.out.println("playing dead...");
                                shutdown();
                            case "reconnect":
                                System.out.println("reconnect message");
                                disconnect();
                                run();//should probably have all this in connect(), but hey this works too
                                break;
                            default:
                                out.println(message);
                        }
                    } catch (InterruptedException e) {
                        System.out.println("ERROR: interruption...");
                        System.out.println("\t"+e.getMessage());
                    }
                }
            }
        }catch(UnknownHostException e){
            System.out.println("ERROR: unknown host");
            //threadStatus="ERROR: unknown host";
            status=Status.ERROR_HOST;
        }catch(IOException e) {
            System.out.println("ERROR: io exception...");
            System.out.println("\t" + e.getMessage());
            //threadStatus="ERROR: I/O exception";
            status=Status.ERROR_IO;
        }
    }
}
