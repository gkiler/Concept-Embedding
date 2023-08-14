package gov.nih.nlm.nls.util.trie;

import java.io.Serializable;

public class Node <T> implements Serializable
{
  /** serialization version unique identifier for this class. */ 
  static final long serialVersionUID = -3583249043139059564L;

  protected char c;
  
  protected T value = null;
	
  protected Node <T> child = null;
  protected Node <T> sibling = null;
}
