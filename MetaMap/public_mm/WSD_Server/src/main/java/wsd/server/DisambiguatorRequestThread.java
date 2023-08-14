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
//    
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
 * DisambiguatorRequestThread class extends java.lang.Thread class and is at the
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

public class DisambiguatorRequestThread extends Thread
{
  /** the list of methods. */
  private String[] fMethods;
  /** the list of weights. */
  private double[] fWeights;
  /** methods to use for request */
  private List requestedMethods;

  /** input request reader.  */
  StringReader reader = null;
  /** DOM tree builder */
  SAXBuilder builder = null;
  /** use keep alive behavior */
  private boolean keepAlive = false;
  /** is processing complete? */
  private boolean ready = false;
  /** semaphore for request thread. */
  private Object semaphore = null;
  /** return result to invoking thread using this variable */
  private StringBuilder outputLine = null;
  
  /** logger */
  private static Logger logger = Logger.getLogger(DisambiguatorRequestThread.class);
  
  /**
   * The constructor method. Created with a socket and debugging information.
   *
   * @param socket  the client socket that the thread will use to communicate
   *                with the WSD Server.
   */
  public DisambiguatorRequestThread(StringReader reader, SAXBuilder builder, Object semaphore)
  {
    super("DisambiguatorRequestThread");
    this.reader = reader;
    this.builder = builder; 
    this.semaphore = semaphore;
    
    /* initialize the requested methods array */
    this.requestedMethods = new ArrayList(10);
  }

  /**
   * Is processing complete?
   * @return true if processing is complete, false if still
   * processing.
   */
  public boolean isReady() {
    return this.ready;
  }
  
  /**
   * Get session type requested by client.
   * @return session type - true if keep alive.
   */
  public boolean keepSessionAlive() {
    return this.keepAlive;
  }

  /**
   * Get result of disambiguation to output to client.
   * <p>
   * Content of variable are only valid if isReady() is true.
   * @return string builder containing output result.
   */
  public StringBuilder getOutputLine() {
    return this.outputLine;
  }

  /**
   * The core method. communicates with
   * disambiguation methods, processes the data and sends the result (if any)
   * back to the WSD Server.
   */
  public void run()
  {
    String inputLine;

    List results = new Vector();
    List resultsToArbitrator = new Vector();
    PreferredNameVector arbitrationResults = null;
    int requestnum = 0;

    StringBuilder outputLine = new StringBuilder();
    try {
      Document doc = this.builder.build(this.reader);
      logger.info("Built the XML tree.");
      Element root = doc.getRootElement();
      
      Namespace ns = root.getNamespace();

      if (ns.getPrefix().equals("rdf"))
	{
	  logger.info("Reading rdf request from the socket..");
	  // handle request (rdf)
	  Iterator childIterator = root.getChildren().iterator();
	  while (childIterator.hasNext()) {
	    Element element = (Element)childIterator.next();
	    if (element.getName().equals("description")) {
	      String about = element.getAttributeValue("about");
	      if (about != null && about.equals("methodslistrequest")) {
		logger.info("Sending methods list.");
		//write the output to the socket
		StringBuilder sb = new StringBuilder();
		sb.append("<?xml version=\"1.0\"?>\n");
		sb.append("<rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"\n");
		sb.append("         xmlns:wsd=\"http://wsd.nlm.nih.gov/wsdserver#\">\n");
		sb.append(" <rdf:description about=\"methodslistresponse\">\n");
		sb.append("  <rdf:Bag>\n");
		Iterator keyIterator = WSDEnvironment.fAvailableMethods.keySet().iterator();
		while (keyIterator.hasNext()) {
		  String methodName = (String)keyIterator.next();
		  String description = null;
		  if (WSDEnvironment.fMethodDescriptions.containsKey(methodName)) {
		    description = (String)WSDEnvironment.fMethodDescriptions.get(methodName);
		  } else {
		    description = methodName;
		  }
		  sb.append("   <rdf:li><wsd:method id=\"")
		    .append(methodName).append("\">")
		    .append(description)
		    .append("      </wsd:method></rdf:li>\n");
		}
		sb.append("  </rdf:Bag>\n");
		sb.append(" </rdf:description>\n");
		sb.append("</rdf:RDF>");
		outputLine = sb;
	      }
	    }
	  }
	} // handle rdf request
      else
	{
	  /* calculate methods and weights */
	  calculateMethodWeights(root.getChild("methods"),ns);
	      
	  /* Get server option list if serveroptionlist tag is
	   * present */
	  Element optionlist = root.getChild("serveroptionlist");
	  if (optionlist != null) {
	    for (Object childObj: optionlist.getChildren()) {
	      Element child = (Element)childObj;
	      /* <serveroption keepalive="true" /> 
	       * set state variable keepAlive based on value of option
	       */
	      if (child.getName().equals("serveroption")) {
		if (child.getAttribute("keepalive") != null) {
		  if (child.getAttributeValue("keepalive").equals("true")) {
		    keepAlive = true;
		  } else {
		    keepAlive = false;
		  }
		}
	      }
	    }
	  }
		  
	  // determine the disambiguation methods to run. Add
	  // requested methods to list.
	  for (int i =0; i < fMethods.length; i ++)
	    {
	      if (WSDEnvironment.fAvailableMethods.containsKey(fMethods[i]))
		{
		  this.requestedMethods.add(fMethods[i]);
		}
	      else
		{
		  logger.error("Cannot find the method: " + fMethods[i]);
		}
	    }
	  logger.info("Determined the methods and weights.");
	  // call the requested methods and perform disambiguation.
	  ListIterator methodIterator = this.requestedMethods.listIterator();
	  while (methodIterator.hasNext()) {
	    String methodName = (String)methodIterator.next();
	    List methodResults = getMatchFromMethod(methodName, doc);
	    ListIterator methodResultsIter = methodResults.listIterator();
	    while (methodResultsIter.hasNext()) {
	      Result res = (Result)methodResultsIter.next();
	      res.setMethodName(methodName);
	    }
	    logger.info("Completed disambiguation with " + methodName);
	    if (methodResults != null)
	      results.add(methodResults);
	    else
	      logger.info(methodName + " did not return any answers.");
	  }

	  // read the disambiguation results and for each ambiguity,
	  // create a list of answers and send them to arbitrator.
	  int k=0;
	  if (results.size() ==  0)
	    {
	      logger.warn("Result list is empty!");
	    }
	  else
	    {
	      String errorCondition = null;
	      while (k < ((List)results.get(0)).size())
		{
		  for (int j=0; j < results.size(); j++)
		    {
		      Result res = (Result)((List)results.get(j)).get(k);

		      /*check to see if there are any errors in the results,
			The result should probably be modified to mark errors*/
		      if (res != null) {
			if ((List)res.getPreferredConceptNames() != null) {
			  if (((List)res.getPreferredConceptNames()).size() > 0) {
			    if (((String)res.getPreferredConceptNames().get(0)).startsWith("[Error")) {
			      errorCondition = (String)res.getPreferredConceptNames().get(0);
			    }
			  }
			  resultsToArbitrator.add(res);
			}
		      }
		    }
		  // add the static part of the disambiation output
		  outputLine.append(((Result)resultsToArbitrator.get(0)).getUi() + "|");
		  outputLine.append(((Result)resultsToArbitrator.get(0)).getUtterancePos() + "|");
		  outputLine.append(((Result)resultsToArbitrator.get(0)).getPhrasePos() + "|");
		  PreferredNameVector candidates =
		    new PreferredNameVector(((Result)resultsToArbitrator.get(0)).getCandidatePreferredConceptNames());
		  outputLine.append(candidates.convertToString() + "|");

		  if (errorCondition == null) {
		    // perform arbitration and write the output
		    arbitrationResults = new PreferredNameVector(arbitrate(resultsToArbitrator));
		    if (arbitrationResults.size() == 0)
		      outputLine.append("[No match found.]|\n");
		    else
		      outputLine.append(arbitrationResults.convertToString() + "|\n");
		  } else {
		    outputLine.append(errorCondition + "|\n");
		  }

		  resultsToArbitrator.clear();
		  k++;
		}
	      results.clear();
	    } /* else results size != 0 */
	} /* else disambiguation request */
      
      synchronized(semaphore) {
	// write outputLine to message for invoking thread 
	this.outputLine = outputLine;
	// return session state to invoking thread
        this.keepAlive = keepAlive;
	ready = true;
	semaphore.notifyAll();
      }
      
      logger.info("Finished processing");
    } catch (JDOMException jde) {
      logger.fatal(jde.getMessage(), jde);
    } catch (NullPointerException npe) {
      logger.fatal(npe.getMessage(), npe);
    } catch (Exception ie) {
      logger.fatal(ie.getMessage(), ie);
    }
  }

  /**
   * Reads the method names and their weights from the DOM tree.
   *
   * @param methodsNode "methods" node of the ambiguity DOM tree.
   * @param ns          the default namespace.
   */
  private void calculateMethodWeights(Element methodsNode, Namespace ns)
  {
    List methodNames = new Vector();
    List weights = new Vector();

    List methodList = methodsNode.getChildren("method", ns);
    ListIterator  methodIterator = methodList.listIterator();
    org.jdom.output.XMLOutputter xmlOutputter = new org.jdom.output.XMLOutputter();
    while (methodIterator.hasNext())
      {
	Element method = (Element)methodIterator.next();
	if (method.getAttributeValue("method_name",ns) != null &&
	    method.getAttributeValue("weight",ns) != null) {
	  if (logger.isDebugEnabled())
	    logger.debug("Method name: " + method.getAttributeValue("method_name",ns));
	  if (logger.isDebugEnabled())
	    logger.debug("Method weight: " + method.getAttributeValue("weight",ns));
	  methodNames.add(method.getAttributeValue("method_name",ns));
	  weights.add(Double.valueOf(method.getAttributeValue("weight",ns)));
	}
      }

    double[] weightArray = new double[weights.size()];
    String[] methodArray = new String[methodNames.size()];
    for (int i = 0; i < methodNames.size(); i++)
      {
	weightArray[i] = ((Double)weights.get(i)).doubleValue();
	methodArray[i] = (String)methodNames.get(i);
      }
    fMethods = methodArray;
    fWeights = weightArray;
  }

  Map<String,DisambiguationMethod> instantiatedMethods = new HashMap<String,DisambiguationMethod>();

  /**
   */
  private DisambiguationMethod instantiateMethod(String methodName)
  {
    String className = (String)WSDEnvironment.fAvailableMethods.get(methodName);
    try
      {
	Class disambiguationMethodClass = Class.forName(className);
	if (this.instantiatedMethods.containsKey(methodName)) {
	  return this.instantiatedMethods.get(methodName);
	} else {
	  DisambiguationMethod method = (DisambiguationMethod)disambiguationMethodClass.newInstance();
	  this.instantiatedMethods.put(methodName, method);
	  return method;
	}
      } catch (java.lang.ClassNotFoundException exception) {
      logger.error("Class " + className +  " not found!");
      exception.printStackTrace(System.err);
    } catch (java.lang.InstantiationException exception) {
      logger.error("Unable to instantiate Class " + className);
      exception.printStackTrace(System.err);
    } catch (java.lang.IllegalAccessException exception) {
      logger.error("Illegal access of Class " + className);
      exception.printStackTrace(System.err);
    }
    return null;
  }

  /**
   * Calls a requested disambiguation Method and returns the results from that
   * method.
   *
   * @param methodName  name of disambiguation method to apply.
   * @param doc         the XML Document that contains the ambiguity data.
   *
   * @return a List of Result objects that represent the best matches for each
   *         ambiguity in the XML Dcocument from the disambiguation method
   */
  private List getMatchFromMethod(String methodName, Document doc)
  {
    List resultsFromDisambMethod = new Vector();
    
    DisambiguationMethod method = instantiateMethod(methodName);
    if (logger.isDebugEnabled())
      logger.debug("Calling " + methodName);
    resultsFromDisambMethod = method.getMatch(doc);
    if (resultsFromDisambMethod == null) {
      return null;
    }
    ListIterator resultIterator = resultsFromDisambMethod.listIterator();
    while (resultIterator.hasNext())
      {
	Result res = (Result)resultIterator.next();
	res.setMethodName(methodName);
	if (logger.isDebugEnabled())
	  logger.debug("Result: " + res.toString());
      }
    return resultsFromDisambMethod;
  }

  /**
   * Sends the results received from the disambiguation methods to the Arbitrator
   * to find the best match among a list of concepts. Uses disambiguation method
   * weights.
   *
   * @param results a Result vector with method name and concepts returned from
   *                the method.
   *
   * @return a List of the highest scored concepts.
   *
   */
  private List arbitrate(List results)
  {
    return (new Arbitrator()).arbitrate(results, fMethods, fWeights);
  }

}

