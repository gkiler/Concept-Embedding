package wsd.util;

/**
 * BSPTuple.java
 *
 *
 * Created: Wed Jul 18 13:10:42 2001
 *
 * @author <a href="mailto:wrogers@nlm.nih.gov">Willie Rogers</a>
 * @version $Id: BSPTuple.java,v 1.1 2006/09/25 18:33:07 wrogers Exp $
 */

public class BSPTuple {
  private String key;
  private Object value;
  /**
   * instantiate new key/value pair object (tuple)
   * @param key   key for tuple.
   * @param value value for key
   */
  public BSPTuple (String key, Object value)
  {
    this.key = key;
    this.value = value;
  }

  public String getKey()
  {
    return this.key;
  }

  public Object getValue()
  {
    return this.value;
  }

  /**
   * Implementation of toString to override default implementation in
   * java.lang.Object.
   * @return string representation of tuple object.
   */  
  public String toString()
  {
    return "key: " + this.key + ", value: " + value;
  }
}// BSPTuple
