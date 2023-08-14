/****************************************************************************
*
*                          PUBLIC DOMAIN NOTICE                         
*         Lister Hill National Center for Biomedical Communications
*                      National Library of Medicine
*                      National Institues of Health
*           United States Department of Health and Human Services
*                                                                         
*  This software is a United States Government Work under the terms of the
*  United States Copyright Act. It was written as part of the authors'
*  official duties as United States Government employees and contractors
*  and thus cannot be copyrighted. This software is freely available
*  to the public for use. The National Library of Medicine and the
*  United States Government have not placed any restriction on its
*  use or reproduction.
*                                                                        
*  Although all reasonable efforts have been taken to ensure the accuracy 
*  and reliability of the software and data, the National Library of Medicine
*  and the United States Government do not and cannot warrant the performance
*  or results that may be obtained by using this software or data.
*  The National Library of Medicine and the U.S. Government disclaim all
*  warranties, expressed or implied, including warranties of performance,
*  merchantability or fitness for any particular purpose.
*                                                                         
*  For full details, please see the MetaMap Terms & Conditions, available at
*  http://metamap.nlm.nih.gov/MMTnCs.shtml.
*
***************************************************************************/

//=== File Prolog ==========================================================
//    This code was developed for National Library of Medicine, Cognitive
//    Science Branch
//
//--- Notes ----------------------------------------------------------------
//
//
//--- Development History --------------------------------------------------
//    Date        Author             Reference
//    ----        ------             ---------
//    04/02/02    Halil Kilicoglu    Initial Version
//
//--- Warning --------------------------------------------------------------
//    This software is property of the National Library of Medicine.
//    Unauthorized use or duplication of this software is
//    strictly prohibited.  Authorized users are subject to the following
//    restrictions:
//    *   Neither the author, their corporation, nor NLM is responsible for
//        any consequence of the use of this software.
//    *   The origin of this software must not be misrepresented either by
//        explicit claim or omission.
//    *   Altered versions of this software must be plainly marked as such.
//    *   This notice may not be removed or altered.
//
//=== End File Prolog ======================================================

package wsd.server;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringReader;

import java.net.Socket;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;
import java.util.Vector;
import java.util.Map;
import java.util.HashMap;

import org.apache.log4j.Logger;

import org.jdom.Document;
import org.jdom.Element;
import org.jdom.JDOMException;
import org.jdom.Namespace;
import org.jdom.input.SAXBuilder;

import wsd.methods.DisambiguationMethod;
import wsd.model.PreferredNameVector;
import wsd.model.Result;
import wsd.util.SocketResourcePool;
import wsd.WSDEnvironment;

/**
 * DisambiguatorServerThread class extends java.lang.Thread class and is at the
 * core of the WSD Server processing. Receives a bunch of ambiguities
 * (all ambiguities from a citation, for example) from WSD Server in XML format,
 * calls specified disambiguation methods, then sends the results from these
 * methods to the Arbitrator to find the best scoring word senses.
 *
 *
 * <P>This code was developed for National Library of Medicine, Cognitive
 * Science Branch.
 *
 * <p>Description: Word Sense Disambiguation</p>
 *
 * @version  04/02/02
 * @author   Halil Kilicoglu
 */

public class DisambiguatorServerThread extends Thread
{
  /** the socket used for communication with WSD Server. */
    private Socket fSocket = null;
  /** the list of methods. */
    private String[] fMethods;
  /** the list of weights. */
    private double[] fWeights;
  /** methods to use for request */
    private List requestedMethods;

  /** logger */
    private static Logger logger = Logger.getLogger(DisambiguatorServerThread.class);

    /**
     * The constructor method. Created with a socket and debugging information.
     *
     * @param socket  the client socket that the thread will use to communicate
     *                with the WSD Server.
     */
    public DisambiguatorServerThread(Socket socket)
    {
	super("DisambiguatorServerThread");
	this.fSocket = socket;

      /* initialize the requested methods array */
	this.requestedMethods = new ArrayList(10);
    }



    /**
     * The core method. Reads data from the socket, communicates with
     * disambiguation methods, processes the data and sends the result (if any)
     * back to the WSD Server.
     */
    public void run()
    {
        String inputLine;
	boolean keepAlive = false; /* keep the connection alive if
				    * true, default is false, close
				    * connection after response. */


        BufferedReader in = null;
        PrintWriter out = null;
        StringReader reader = null;

        List results = new Vector();
        List resultsToArbitrator = new Vector();
        PreferredNameVector arbitrationResults = null;
        int requestnum = 0;

	try
        {
	    if (logger.isDebugEnabled()) {
	       logger.debug("Receiving data from socket originating at: " +
			    fSocket.getInetAddress().toString());
	    }
	    logger.info("Session Begin: " + fSocket.getInetAddress().toString());
            out = new PrintWriter(fSocket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(fSocket.getInputStream()));

	    if (in == null) {
	      logger.error("socket input stream in is null.");
	    } 
	    SAXBuilder builder = new SAXBuilder(false);
	    while (true) {
	      StringBuffer entireText = new StringBuffer();
	      // first read the entire string coming from the socket
	      if (fSocket.isClosed()) break;
	      if (in != null) {
		while (((inputLine = in.readLine()) != null) && (inputLine.length() > 0)) {
		  if (inputLine != null) {
		    entireText.append(inputLine.trim());
		  } 
		}
	      }
	      if (logger.isDebugEnabled()) {
		logger.debug("entireText: " + entireText);

	      // byte[] byteArray = entireText.toString().getBytes();
	      // logger.debug("byte array of entireText: " + byteArray);
	      // int l = 0;
	      // for (byte aByte: byteArray) {
	      // 	logger.debug(l + ": " + aByte);
	      // 	l++;
	      // }
	      }

	      // check for empty input string buffer, if empty then client
	      // has probably disconnected.
	      if (entireText.toString().length() == 0) {
		if (logger.isDebugEnabled()) {
		  logger.debug("Empty input buffer, client has probably disconnected.");
		  logger.debug("Socket.isClosed: " + fSocket.isClosed() +
			       ", Socket.isBound: " + fSocket.isBound() +
			       ", in.ready() " + in.ready());
		}
		break;
	      }

	      // create a DOM Tree from the incoming text
	      if (logger.isDebugEnabled())
                logger.debug("Text[" + entireText.length() + "] from socket: " + entireText);
	      reader = new StringReader(entireText.toString());

	      // run request in a separate thread.
	      Object semaphore = new Object();
	      DisambiguatorRequestThread requestThread = 
		new DisambiguatorRequestThread(reader, builder, semaphore);
	      requestThread.run();
              // requestThread.join();

              
              // wait for processing thread to complete and then get result and send it to client
              // if request requested persistant session (keepAlive) then keep socket open and process next request.
	      synchronized(semaphore) {
		while (!requestThread.isReady()) {
		  semaphore.wait();
		}
	      }

	      StringBuilder outputLine = requestThread.getOutputLine();
              keepAlive = requestThread.keepSessionAlive();

	      //write the output to the socket
	      if (logger.isDebugEnabled()) {
		logger.debug("Output to the socket: " + 
			     "<Response>" + outputLine.toString().trim() + "</Response>");
		logger.debug("keepAlive: " + keepAlive);
              }
	      if (keepAlive) {
		/* If we are keeping alive the connection,
		 * send a null (0) at the end of the message
		 * to inform the client that this is the end
		 * of the message. */
		out.print("<Response>" + outputLine.toString().trim() + "</Response>\n\0");
		// if ((requestnum % 500) == 0) {
		//    System.gc(); // encourage the garbage collector to run.
		// }
		// requestnum++;
	      } else {
		/* Send the message in the previous (normal?)
		 * manner if we are not keeping the connection
		 * alive. */
		out.print("<Response>" + outputLine.toString() + "</Response>\n");
	      }
	      out.flush();
	      logger.info("Output written to the socket.");


	      /** if keepAlive is false, then break and close connection. */
	      if (keepAlive == false) break;
	      /** if socket has closed then kill this thread. */
	      if (fSocket.isClosed()) { logger.warn("socket is closed!!"); break; }
	    }

	    out.close();
	    in.close();
	    fSocket.close();
	    
	    logger.info("Input and output streams and the socket is closed.");
	    // if (logger.isDebugEnabled())
            // {
            //     logger.debug("Free socket resources: " + SocketResourcePool.getInstance().getFreeSocketResourceCount());
            //     logger.debug("Used socket resources: " + SocketResourcePool.getInstance().getUsedSocketResourceCount());
            //     logger.debug("Broken socket resources: " + SocketResourcePool.getInstance().getBrokenSocketResourceCount());
            // }

	}
	catch (NullPointerException npe)
	{
            logger.fatal(npe.getMessage(), npe);
	}
        catch (IOException ioe)
        {
            logger.fatal(ioe.getMessage(), ioe);
	} catch (Exception ie) 
        {
            logger.fatal(ie.getMessage(), ie);
        }
    }
}

