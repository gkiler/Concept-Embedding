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

package wsd.model;

import java.util.List;

/**
 * This class represents a result from a disambiguation method. A disambiguation
 * result has six elements: the method name, the utterance id, the utterance position,
 * the noun phrase position, the candidate senses and the selected senses. Note
 * that a method can return more than one sense of an ambiguity, therefore a
 * disambiguation method returns a List of Result objects.
 *
 * <P>This code was developed for National Library of Medicine, Cognitive
 * Science Branch.
 *
 * <p>Description: Word Sense Disambiguation</p>
 *
 * @version  04/02/02
 * @author   Halil Kilicoglu
 */
public class Result
{
  /** the name of the method */
  private String fMethodName;
  /** the utterance ui */
  private String fUi;
  /** the utterance position */
  private int fUtterancePos;
  /** the noun phrase position */
  private int fPhrasePos;
  /** the candidate preferred concept name list */
  private List fCandidatePreferredConceptNames;
  /** the preferred concept name list */
  private List fPreferredConceptNames;

  /**
   * Default constructor. No parameters.
   */
  public Result()
  {
  }

  /**
   * Constructor. All member fields are set.
   *
   * @param methodName                     disambiguation method name
   * @param ui                             utterance id
   * @param utterancePos                   utterance position in the citation
   * @param phrasePos                      noun phrase position in the utterance
   * @param candidatePreferredConceptNames candidate preferred concepts for this ambiguity
   * @param preferredConceptNames          selected preferred concepts for this ambiguity
   *
   */
  public Result(String methodName,
                String ui,
                int utterancePos,
                int phrasePos,
                List candidatePreferredConceptNames,
                List preferredConceptNames)
  {
      fMethodName = methodName;
      fUi = ui;
      fUtterancePos = utterancePos;
      fPhrasePos = phrasePos;
      fCandidatePreferredConceptNames = candidatePreferredConceptNames;
      fPreferredConceptNames = preferredConceptNames;
  }

  /**
   * set() method for the method name.
   *
   * @param methodName  disambiguation method name
   */
  public void setMethodName(String methodName)
  {
      fMethodName = methodName;
  }

 /**
   * set() method for utterance id.
   *
   * @param ui  utterance id
   */
  public void setUi(String ui)
  {
      fUi = ui;
  }

 /**
   * set() method for utterance position.
   *
   * @param utterancePos  utterance position
   */
  public void setUtterancePos(int utterancePos)
  {
      fUtterancePos = utterancePos;
  }

 /**
   * set() method for noun phrase position.
   *
   * @param phrasePos  noun phrase position
   */
  public void setPhrasePos(int phrasePos)
  {
      fPhrasePos = phrasePos;
  }

  /**
   * set() method for the candidate preferred concept list.
   *
   * @param candidataPreferredConceptNames  a list of preferred names of concepts.
   */
  public void setCandidatePreferredConceptNames(List candidatePreferredConceptNames)
  {
      fCandidatePreferredConceptNames = candidatePreferredConceptNames;
  }

  /**
   * set() method for the preferred concept list.
   *
   * @param preferredConceptNames  a list of preferred names of concepts.
   */
  public void setPreferredConceptNames(List preferredConceptNames)
  {
      fPreferredConceptNames = preferredConceptNames;
  }

  /**
   * get() method for the method name.
   *
   * @return  disambiguation method name associated with this Result object.
   */
  public String getMethodName()
  {
      return fMethodName;
  }

  /**
   * get() method for the utterance id.
   *
   * @return  the id of the utterance with the ambiguity.
   */
  public String getUi()
  {
      return fUi;
  }

  /**
   * get() method for the utterance position.
   *
   * @return  the position of the utterance with the ambiguity in the citation.
   */
  public int getUtterancePos()
  {
      return fUtterancePos;
  }

  /**
   * get() method for the noun phrase position.
   *
   * @return  the position of the noun phrase with the ambiguity in the utterance.
   */
  public int getPhrasePos()
  {
      return fPhrasePos;
  }

  /**
   * get() method for the candidate preferred name list of the concept.
   *
   * @return  the candidate preferred name list of the concept.
   */
  public List getCandidatePreferredConceptNames()
  {
      return fCandidatePreferredConceptNames;
  }

  /**
   * get() method for the selected preferred name list of the concept.
   *
   * @return  the selected preferred name list of the concept.
   */
  public List getPreferredConceptNames()
  {
      return fPreferredConceptNames;
  }

  /**
   * converts a Result object into its String representation. The string representation
   * has the following format:
   * <p><i>Method name|utterance id|utterance position|noun phrase position|[list of candidates]|
   * [list of selected concepts]</i>
   *
   * @return  the String representation of the Result object.
   */
  public String toString()
  {
      StringBuffer buf = new StringBuffer();
      PreferredNameVector candidates = new PreferredNameVector(fCandidatePreferredConceptNames);
      PreferredNameVector matches = new PreferredNameVector(fPreferredConceptNames);
      buf.append(fMethodName + "|" + fUi + "|" + fUtterancePos + "|" + fPhrasePos + "|" +
                  candidates.convertToString() + "|" + matches.convertToString());

      return buf.toString().trim();
  }


}
