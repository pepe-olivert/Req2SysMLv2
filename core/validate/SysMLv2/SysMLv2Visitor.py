# Generated from SysMLv2.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SysMLv2Parser import SysMLv2Parser
else:
    from SysMLv2Parser import SysMLv2Parser

# This class defines a complete generic visitor for a parse tree produced by SysMLv2Parser.

class SysMLv2Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by SysMLv2Parser#entryRuleRootNamespace.
    def visitEntryRuleRootNamespace(self, ctx:SysMLv2Parser.EntryRuleRootNamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRootNamespace.
    def visitRuleRootNamespace(self, ctx:SysMLv2Parser.RuleRootNamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleIdentification1.
    def visitRuleIdentification1(self, ctx:SysMLv2Parser.RuleIdentification1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleIdentification2.
    def visitRuleIdentification2(self, ctx:SysMLv2Parser.RuleIdentification2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRelationshipBody1.
    def visitRuleRelationshipBody1(self, ctx:SysMLv2Parser.RuleRelationshipBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRelationshipBody2.
    def visitRuleRelationshipBody2(self, ctx:SysMLv2Parser.RuleRelationshipBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDependency.
    def visitRuleDependency(self, ctx:SysMLv2Parser.RuleDependencyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnnotation.
    def visitRuleAnnotation(self, ctx:SysMLv2Parser.RuleAnnotationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedAnnotation.
    def visitRuleOwnedAnnotation(self, ctx:SysMLv2Parser.RuleOwnedAnnotationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnnotatingMember.
    def visitRuleAnnotatingMember(self, ctx:SysMLv2Parser.RuleAnnotatingMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnnotatingElement1.
    def visitRuleAnnotatingElement1(self, ctx:SysMLv2Parser.RuleAnnotatingElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnnotatingElement2.
    def visitRuleAnnotatingElement2(self, ctx:SysMLv2Parser.RuleAnnotatingElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnnotatingElement3.
    def visitRuleAnnotatingElement3(self, ctx:SysMLv2Parser.RuleAnnotatingElement3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnnotatingElement4.
    def visitRuleAnnotatingElement4(self, ctx:SysMLv2Parser.RuleAnnotatingElement4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleComment.
    def visitRuleComment(self, ctx:SysMLv2Parser.RuleCommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDocumentation.
    def visitRuleDocumentation(self, ctx:SysMLv2Parser.RuleDocumentationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTextualRepresentation.
    def visitRuleTextualRepresentation(self, ctx:SysMLv2Parser.RuleTextualRepresentationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataKeyword.
    def visitRuleMetadataKeyword(self, ctx:SysMLv2Parser.RuleMetadataKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataDefKeyword.
    def visitRuleMetadataDefKeyword(self, ctx:SysMLv2Parser.RuleMetadataDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataUsageKeyword1.
    def visitRuleMetadataUsageKeyword1(self, ctx:SysMLv2Parser.RuleMetadataUsageKeyword1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataUsageKeyword2.
    def visitRuleMetadataUsageKeyword2(self, ctx:SysMLv2Parser.RuleMetadataUsageKeyword2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataDefinition.
    def visitRuleMetadataDefinition(self, ctx:SysMLv2Parser.RuleMetadataDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePrefixMetadataAnnotation.
    def visitRulePrefixMetadataAnnotation(self, ctx:SysMLv2Parser.RulePrefixMetadataAnnotationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePrefixMetadataMember.
    def visitRulePrefixMetadataMember(self, ctx:SysMLv2Parser.RulePrefixMetadataMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePrefixMetadataUsage.
    def visitRulePrefixMetadataUsage(self, ctx:SysMLv2Parser.RulePrefixMetadataUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataUsage.
    def visitRuleMetadataUsage(self, ctx:SysMLv2Parser.RuleMetadataUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataUsageDeclaration.
    def visitRuleMetadataUsageDeclaration(self, ctx:SysMLv2Parser.RuleMetadataUsageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataTyping.
    def visitRuleMetadataTyping(self, ctx:SysMLv2Parser.RuleMetadataTypingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataBody1.
    def visitRuleMetadataBody1(self, ctx:SysMLv2Parser.RuleMetadataBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataBody2.
    def visitRuleMetadataBody2(self, ctx:SysMLv2Parser.RuleMetadataBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataBodyUsageMember.
    def visitRuleMetadataBodyUsageMember(self, ctx:SysMLv2Parser.RuleMetadataBodyUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataBodyUsage.
    def visitRuleMetadataBodyUsage(self, ctx:SysMLv2Parser.RuleMetadataBodyUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePackage.
    def visitRulePackage(self, ctx:SysMLv2Parser.RulePackageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLibraryPackage.
    def visitRuleLibraryPackage(self, ctx:SysMLv2Parser.RuleLibraryPackageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePackageDeclaration.
    def visitRulePackageDeclaration(self, ctx:SysMLv2Parser.RulePackageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePackageBody1.
    def visitRulePackageBody1(self, ctx:SysMLv2Parser.RulePackageBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePackageBody2.
    def visitRulePackageBody2(self, ctx:SysMLv2Parser.RulePackageBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePackageBodyElement1.
    def visitRulePackageBodyElement1(self, ctx:SysMLv2Parser.RulePackageBodyElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePackageBodyElement2.
    def visitRulePackageBodyElement2(self, ctx:SysMLv2Parser.RulePackageBodyElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePackageBodyElement3.
    def visitRulePackageBodyElement3(self, ctx:SysMLv2Parser.RulePackageBodyElement3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePackageBodyElement4.
    def visitRulePackageBodyElement4(self, ctx:SysMLv2Parser.RulePackageBodyElement4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMemberPrefix.
    def visitRuleMemberPrefix(self, ctx:SysMLv2Parser.RuleMemberPrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePackageMember.
    def visitRulePackageMember(self, ctx:SysMLv2Parser.RulePackageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleElementFilterMember.
    def visitRuleElementFilterMember(self, ctx:SysMLv2Parser.RuleElementFilterMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAliasMember.
    def visitRuleAliasMember(self, ctx:SysMLv2Parser.RuleAliasMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleImportPrefix.
    def visitRuleImportPrefix(self, ctx:SysMLv2Parser.RuleImportPrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleImport.
    def visitRuleImport(self, ctx:SysMLv2Parser.RuleImportContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMembershipImport.
    def visitRuleMembershipImport(self, ctx:SysMLv2Parser.RuleMembershipImportContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleImportedMembership.
    def visitRuleImportedMembership(self, ctx:SysMLv2Parser.RuleImportedMembershipContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNamespaceImport.
    def visitRuleNamespaceImport(self, ctx:SysMLv2Parser.RuleNamespaceImportContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleImportedNamespace.
    def visitRuleImportedNamespace(self, ctx:SysMLv2Parser.RuleImportedNamespaceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFilterPackage.
    def visitRuleFilterPackage(self, ctx:SysMLv2Parser.RuleFilterPackageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFilterPackageImport1.
    def visitRuleFilterPackageImport1(self, ctx:SysMLv2Parser.RuleFilterPackageImport1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFilterPackageImport2.
    def visitRuleFilterPackageImport2(self, ctx:SysMLv2Parser.RuleFilterPackageImport2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFilterPackageMembershipImport.
    def visitRuleFilterPackageMembershipImport(self, ctx:SysMLv2Parser.RuleFilterPackageMembershipImportContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFilterPackageNamespaceImport.
    def visitRuleFilterPackageNamespaceImport(self, ctx:SysMLv2Parser.RuleFilterPackageNamespaceImportContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFilterPackageMember.
    def visitRuleFilterPackageMember(self, ctx:SysMLv2Parser.RuleFilterPackageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement1.
    def visitRuleDefinitionElement1(self, ctx:SysMLv2Parser.RuleDefinitionElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement2.
    def visitRuleDefinitionElement2(self, ctx:SysMLv2Parser.RuleDefinitionElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement3.
    def visitRuleDefinitionElement3(self, ctx:SysMLv2Parser.RuleDefinitionElement3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement4.
    def visitRuleDefinitionElement4(self, ctx:SysMLv2Parser.RuleDefinitionElement4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement5.
    def visitRuleDefinitionElement5(self, ctx:SysMLv2Parser.RuleDefinitionElement5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement6.
    def visitRuleDefinitionElement6(self, ctx:SysMLv2Parser.RuleDefinitionElement6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement7.
    def visitRuleDefinitionElement7(self, ctx:SysMLv2Parser.RuleDefinitionElement7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement8.
    def visitRuleDefinitionElement8(self, ctx:SysMLv2Parser.RuleDefinitionElement8Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement9.
    def visitRuleDefinitionElement9(self, ctx:SysMLv2Parser.RuleDefinitionElement9Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement10.
    def visitRuleDefinitionElement10(self, ctx:SysMLv2Parser.RuleDefinitionElement10Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement11.
    def visitRuleDefinitionElement11(self, ctx:SysMLv2Parser.RuleDefinitionElement11Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement12.
    def visitRuleDefinitionElement12(self, ctx:SysMLv2Parser.RuleDefinitionElement12Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement13.
    def visitRuleDefinitionElement13(self, ctx:SysMLv2Parser.RuleDefinitionElement13Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement14.
    def visitRuleDefinitionElement14(self, ctx:SysMLv2Parser.RuleDefinitionElement14Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement15.
    def visitRuleDefinitionElement15(self, ctx:SysMLv2Parser.RuleDefinitionElement15Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement16.
    def visitRuleDefinitionElement16(self, ctx:SysMLv2Parser.RuleDefinitionElement16Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement17.
    def visitRuleDefinitionElement17(self, ctx:SysMLv2Parser.RuleDefinitionElement17Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement18.
    def visitRuleDefinitionElement18(self, ctx:SysMLv2Parser.RuleDefinitionElement18Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement19.
    def visitRuleDefinitionElement19(self, ctx:SysMLv2Parser.RuleDefinitionElement19Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement20.
    def visitRuleDefinitionElement20(self, ctx:SysMLv2Parser.RuleDefinitionElement20Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement21.
    def visitRuleDefinitionElement21(self, ctx:SysMLv2Parser.RuleDefinitionElement21Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement22.
    def visitRuleDefinitionElement22(self, ctx:SysMLv2Parser.RuleDefinitionElement22Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement23.
    def visitRuleDefinitionElement23(self, ctx:SysMLv2Parser.RuleDefinitionElement23Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement24.
    def visitRuleDefinitionElement24(self, ctx:SysMLv2Parser.RuleDefinitionElement24Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement25.
    def visitRuleDefinitionElement25(self, ctx:SysMLv2Parser.RuleDefinitionElement25Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement26.
    def visitRuleDefinitionElement26(self, ctx:SysMLv2Parser.RuleDefinitionElement26Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement27.
    def visitRuleDefinitionElement27(self, ctx:SysMLv2Parser.RuleDefinitionElement27Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement28.
    def visitRuleDefinitionElement28(self, ctx:SysMLv2Parser.RuleDefinitionElement28Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement29.
    def visitRuleDefinitionElement29(self, ctx:SysMLv2Parser.RuleDefinitionElement29Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionElement30.
    def visitRuleDefinitionElement30(self, ctx:SysMLv2Parser.RuleDefinitionElement30Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUsageElement1.
    def visitRuleUsageElement1(self, ctx:SysMLv2Parser.RuleUsageElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUsageElement2.
    def visitRuleUsageElement2(self, ctx:SysMLv2Parser.RuleUsageElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSubclassificationPart.
    def visitRuleSubclassificationPart(self, ctx:SysMLv2Parser.RuleSubclassificationPartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSpecializesKeyword1.
    def visitRuleSpecializesKeyword1(self, ctx:SysMLv2Parser.RuleSpecializesKeyword1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSpecializesKeyword2.
    def visitRuleSpecializesKeyword2(self, ctx:SysMLv2Parser.RuleSpecializesKeyword2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedSubclassification.
    def visitRuleOwnedSubclassification(self, ctx:SysMLv2Parser.RuleOwnedSubclassificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureDeclaration1.
    def visitRuleFeatureDeclaration1(self, ctx:SysMLv2Parser.RuleFeatureDeclaration1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureDeclaration2.
    def visitRuleFeatureDeclaration2(self, ctx:SysMLv2Parser.RuleFeatureDeclaration2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureSpecializationPart1.
    def visitRuleFeatureSpecializationPart1(self, ctx:SysMLv2Parser.RuleFeatureSpecializationPart1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureSpecializationPart2.
    def visitRuleFeatureSpecializationPart2(self, ctx:SysMLv2Parser.RuleFeatureSpecializationPart2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicityPart1.
    def visitRuleMultiplicityPart1(self, ctx:SysMLv2Parser.RuleMultiplicityPart1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicityPart2.
    def visitRuleMultiplicityPart2(self, ctx:SysMLv2Parser.RuleMultiplicityPart2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureSpecialization1.
    def visitRuleFeatureSpecialization1(self, ctx:SysMLv2Parser.RuleFeatureSpecialization1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureSpecialization2.
    def visitRuleFeatureSpecialization2(self, ctx:SysMLv2Parser.RuleFeatureSpecialization2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureSpecialization3.
    def visitRuleFeatureSpecialization3(self, ctx:SysMLv2Parser.RuleFeatureSpecialization3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureSpecialization4.
    def visitRuleFeatureSpecialization4(self, ctx:SysMLv2Parser.RuleFeatureSpecialization4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureSpecialization5.
    def visitRuleFeatureSpecialization5(self, ctx:SysMLv2Parser.RuleFeatureSpecialization5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTypings.
    def visitRuleTypings(self, ctx:SysMLv2Parser.RuleTypingsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTypedBy.
    def visitRuleTypedBy(self, ctx:SysMLv2Parser.RuleTypedByContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinedByKeyword1.
    def visitRuleDefinedByKeyword1(self, ctx:SysMLv2Parser.RuleDefinedByKeyword1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinedByKeyword2.
    def visitRuleDefinedByKeyword2(self, ctx:SysMLv2Parser.RuleDefinedByKeyword2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSubsettings.
    def visitRuleSubsettings(self, ctx:SysMLv2Parser.RuleSubsettingsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSubsets.
    def visitRuleSubsets(self, ctx:SysMLv2Parser.RuleSubsetsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSubsetsKeyword1.
    def visitRuleSubsetsKeyword1(self, ctx:SysMLv2Parser.RuleSubsetsKeyword1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSubsetsKeyword2.
    def visitRuleSubsetsKeyword2(self, ctx:SysMLv2Parser.RuleSubsetsKeyword2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleReferences.
    def visitRuleReferences(self, ctx:SysMLv2Parser.RuleReferencesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleReferencesKeyword1.
    def visitRuleReferencesKeyword1(self, ctx:SysMLv2Parser.RuleReferencesKeyword1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleReferencesKeyword2.
    def visitRuleReferencesKeyword2(self, ctx:SysMLv2Parser.RuleReferencesKeyword2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCrosses.
    def visitRuleCrosses(self, ctx:SysMLv2Parser.RuleCrossesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCrossesKeyword1.
    def visitRuleCrossesKeyword1(self, ctx:SysMLv2Parser.RuleCrossesKeyword1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCrossesKeyword2.
    def visitRuleCrossesKeyword2(self, ctx:SysMLv2Parser.RuleCrossesKeyword2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRedefines.
    def visitRuleRedefines(self, ctx:SysMLv2Parser.RuleRedefinesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRedefinesKeyword1.
    def visitRuleRedefinesKeyword1(self, ctx:SysMLv2Parser.RuleRedefinesKeyword1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRedefinesKeyword2.
    def visitRuleRedefinesKeyword2(self, ctx:SysMLv2Parser.RuleRedefinesKeyword2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureTyping1.
    def visitRuleFeatureTyping1(self, ctx:SysMLv2Parser.RuleFeatureTyping1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureTyping2.
    def visitRuleFeatureTyping2(self, ctx:SysMLv2Parser.RuleFeatureTyping2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedSubsetting1.
    def visitRuleOwnedSubsetting1(self, ctx:SysMLv2Parser.RuleOwnedSubsetting1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedSubsetting2.
    def visitRuleOwnedSubsetting2(self, ctx:SysMLv2Parser.RuleOwnedSubsetting2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedReferenceSubsetting1.
    def visitRuleOwnedReferenceSubsetting1(self, ctx:SysMLv2Parser.RuleOwnedReferenceSubsetting1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedReferenceSubsetting2.
    def visitRuleOwnedReferenceSubsetting2(self, ctx:SysMLv2Parser.RuleOwnedReferenceSubsetting2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedCrossSubsetting1.
    def visitRuleOwnedCrossSubsetting1(self, ctx:SysMLv2Parser.RuleOwnedCrossSubsetting1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedCrossSubsetting2.
    def visitRuleOwnedCrossSubsetting2(self, ctx:SysMLv2Parser.RuleOwnedCrossSubsetting2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRedefinitions.
    def visitRuleRedefinitions(self, ctx:SysMLv2Parser.RuleRedefinitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedRedefinition1.
    def visitRuleOwnedRedefinition1(self, ctx:SysMLv2Parser.RuleOwnedRedefinition1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedRedefinition2.
    def visitRuleOwnedRedefinition2(self, ctx:SysMLv2Parser.RuleOwnedRedefinition2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedMultiplicity.
    def visitRuleOwnedMultiplicity(self, ctx:SysMLv2Parser.RuleOwnedMultiplicityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicityRange.
    def visitRuleMultiplicityRange(self, ctx:SysMLv2Parser.RuleMultiplicityRangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicityExpressionMember.
    def visitRuleMultiplicityExpressionMember(self, ctx:SysMLv2Parser.RuleMultiplicityExpressionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBasicDefinitionPrefix1.
    def visitRuleBasicDefinitionPrefix1(self, ctx:SysMLv2Parser.RuleBasicDefinitionPrefix1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBasicDefinitionPrefix2.
    def visitRuleBasicDefinitionPrefix2(self, ctx:SysMLv2Parser.RuleBasicDefinitionPrefix2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionExtensionKeyword.
    def visitRuleDefinitionExtensionKeyword(self, ctx:SysMLv2Parser.RuleDefinitionExtensionKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionPrefix.
    def visitRuleDefinitionPrefix(self, ctx:SysMLv2Parser.RuleDefinitionPrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinition.
    def visitRuleDefinition(self, ctx:SysMLv2Parser.RuleDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionDeclaration.
    def visitRuleDefinitionDeclaration(self, ctx:SysMLv2Parser.RuleDefinitionDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionBody1.
    def visitRuleDefinitionBody1(self, ctx:SysMLv2Parser.RuleDefinitionBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionBody2.
    def visitRuleDefinitionBody2(self, ctx:SysMLv2Parser.RuleDefinitionBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionBodyItem1.
    def visitRuleDefinitionBodyItem1(self, ctx:SysMLv2Parser.RuleDefinitionBodyItem1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionBodyItem2.
    def visitRuleDefinitionBodyItem2(self, ctx:SysMLv2Parser.RuleDefinitionBodyItem2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionBodyItem3.
    def visitRuleDefinitionBodyItem3(self, ctx:SysMLv2Parser.RuleDefinitionBodyItem3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionBodyItem4.
    def visitRuleDefinitionBodyItem4(self, ctx:SysMLv2Parser.RuleDefinitionBodyItem4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionBodyItem5.
    def visitRuleDefinitionBodyItem5(self, ctx:SysMLv2Parser.RuleDefinitionBodyItem5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionBodyItem6.
    def visitRuleDefinitionBodyItem6(self, ctx:SysMLv2Parser.RuleDefinitionBodyItem6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefinitionMember.
    def visitRuleDefinitionMember(self, ctx:SysMLv2Parser.RuleDefinitionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageMember.
    def visitRuleVariantUsageMember(self, ctx:SysMLv2Parser.RuleVariantUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNonOccurrenceUsageMember.
    def visitRuleNonOccurrenceUsageMember(self, ctx:SysMLv2Parser.RuleNonOccurrenceUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceUsageMember.
    def visitRuleOccurrenceUsageMember(self, ctx:SysMLv2Parser.RuleOccurrenceUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageMember.
    def visitRuleStructureUsageMember(self, ctx:SysMLv2Parser.RuleStructureUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageMember.
    def visitRuleBehaviorUsageMember(self, ctx:SysMLv2Parser.RuleBehaviorUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRefPrefix.
    def visitRuleRefPrefix(self, ctx:SysMLv2Parser.RuleRefPrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBasicUsagePrefix.
    def visitRuleBasicUsagePrefix(self, ctx:SysMLv2Parser.RuleBasicUsagePrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEndUsagePrefix.
    def visitRuleEndUsagePrefix(self, ctx:SysMLv2Parser.RuleEndUsagePrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUnextendedUsagePrefix1.
    def visitRuleUnextendedUsagePrefix1(self, ctx:SysMLv2Parser.RuleUnextendedUsagePrefix1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUnextendedUsagePrefix2.
    def visitRuleUnextendedUsagePrefix2(self, ctx:SysMLv2Parser.RuleUnextendedUsagePrefix2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUsageExtensionKeyword.
    def visitRuleUsageExtensionKeyword(self, ctx:SysMLv2Parser.RuleUsageExtensionKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUsagePrefix.
    def visitRuleUsagePrefix(self, ctx:SysMLv2Parser.RuleUsagePrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedCrossFeatureMember.
    def visitRuleOwnedCrossFeatureMember(self, ctx:SysMLv2Parser.RuleOwnedCrossFeatureMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedCrossFeature.
    def visitRuleOwnedCrossFeature(self, ctx:SysMLv2Parser.RuleOwnedCrossFeatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUsage.
    def visitRuleUsage(self, ctx:SysMLv2Parser.RuleUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUsageDeclaration.
    def visitRuleUsageDeclaration(self, ctx:SysMLv2Parser.RuleUsageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUsageCompletion.
    def visitRuleUsageCompletion(self, ctx:SysMLv2Parser.RuleUsageCompletionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUsageBody.
    def visitRuleUsageBody(self, ctx:SysMLv2Parser.RuleUsageBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleValuePart.
    def visitRuleValuePart(self, ctx:SysMLv2Parser.RuleValuePartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureValue.
    def visitRuleFeatureValue(self, ctx:SysMLv2Parser.RuleFeatureValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleReferenceKeyword.
    def visitRuleReferenceKeyword(self, ctx:SysMLv2Parser.RuleReferenceKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleReferenceUsageKeyword.
    def visitRuleReferenceUsageKeyword(self, ctx:SysMLv2Parser.RuleReferenceUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefaultReferenceUsage.
    def visitRuleDefaultReferenceUsage(self, ctx:SysMLv2Parser.RuleDefaultReferenceUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleReferenceUsage.
    def visitRuleReferenceUsage(self, ctx:SysMLv2Parser.RuleReferenceUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantReference.
    def visitRuleVariantReference(self, ctx:SysMLv2Parser.RuleVariantReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNonOccurrenceUsageElement1.
    def visitRuleNonOccurrenceUsageElement1(self, ctx:SysMLv2Parser.RuleNonOccurrenceUsageElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNonOccurrenceUsageElement2.
    def visitRuleNonOccurrenceUsageElement2(self, ctx:SysMLv2Parser.RuleNonOccurrenceUsageElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNonOccurrenceUsageElement3.
    def visitRuleNonOccurrenceUsageElement3(self, ctx:SysMLv2Parser.RuleNonOccurrenceUsageElement3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNonOccurrenceUsageElement4.
    def visitRuleNonOccurrenceUsageElement4(self, ctx:SysMLv2Parser.RuleNonOccurrenceUsageElement4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNonOccurrenceUsageElement5.
    def visitRuleNonOccurrenceUsageElement5(self, ctx:SysMLv2Parser.RuleNonOccurrenceUsageElement5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNonOccurrenceUsageElement6.
    def visitRuleNonOccurrenceUsageElement6(self, ctx:SysMLv2Parser.RuleNonOccurrenceUsageElement6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNonOccurrenceUsageElement7.
    def visitRuleNonOccurrenceUsageElement7(self, ctx:SysMLv2Parser.RuleNonOccurrenceUsageElement7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceUsageElement1.
    def visitRuleOccurrenceUsageElement1(self, ctx:SysMLv2Parser.RuleOccurrenceUsageElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceUsageElement2.
    def visitRuleOccurrenceUsageElement2(self, ctx:SysMLv2Parser.RuleOccurrenceUsageElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement1.
    def visitRuleStructureUsageElement1(self, ctx:SysMLv2Parser.RuleStructureUsageElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement2.
    def visitRuleStructureUsageElement2(self, ctx:SysMLv2Parser.RuleStructureUsageElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement3.
    def visitRuleStructureUsageElement3(self, ctx:SysMLv2Parser.RuleStructureUsageElement3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement4.
    def visitRuleStructureUsageElement4(self, ctx:SysMLv2Parser.RuleStructureUsageElement4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement5.
    def visitRuleStructureUsageElement5(self, ctx:SysMLv2Parser.RuleStructureUsageElement5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement6.
    def visitRuleStructureUsageElement6(self, ctx:SysMLv2Parser.RuleStructureUsageElement6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement7.
    def visitRuleStructureUsageElement7(self, ctx:SysMLv2Parser.RuleStructureUsageElement7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement8.
    def visitRuleStructureUsageElement8(self, ctx:SysMLv2Parser.RuleStructureUsageElement8Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement9.
    def visitRuleStructureUsageElement9(self, ctx:SysMLv2Parser.RuleStructureUsageElement9Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement10.
    def visitRuleStructureUsageElement10(self, ctx:SysMLv2Parser.RuleStructureUsageElement10Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement11.
    def visitRuleStructureUsageElement11(self, ctx:SysMLv2Parser.RuleStructureUsageElement11Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement12.
    def visitRuleStructureUsageElement12(self, ctx:SysMLv2Parser.RuleStructureUsageElement12Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement13.
    def visitRuleStructureUsageElement13(self, ctx:SysMLv2Parser.RuleStructureUsageElement13Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement14.
    def visitRuleStructureUsageElement14(self, ctx:SysMLv2Parser.RuleStructureUsageElement14Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStructureUsageElement15.
    def visitRuleStructureUsageElement15(self, ctx:SysMLv2Parser.RuleStructureUsageElement15Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement1.
    def visitRuleBehaviorUsageElement1(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement2.
    def visitRuleBehaviorUsageElement2(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement3.
    def visitRuleBehaviorUsageElement3(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement4.
    def visitRuleBehaviorUsageElement4(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement5.
    def visitRuleBehaviorUsageElement5(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement6.
    def visitRuleBehaviorUsageElement6(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement7.
    def visitRuleBehaviorUsageElement7(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement8.
    def visitRuleBehaviorUsageElement8(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement8Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement9.
    def visitRuleBehaviorUsageElement9(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement9Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement10.
    def visitRuleBehaviorUsageElement10(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement10Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement11.
    def visitRuleBehaviorUsageElement11(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement11Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement12.
    def visitRuleBehaviorUsageElement12(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement12Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement13.
    def visitRuleBehaviorUsageElement13(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement13Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement14.
    def visitRuleBehaviorUsageElement14(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement14Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement15.
    def visitRuleBehaviorUsageElement15(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement15Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBehaviorUsageElement16.
    def visitRuleBehaviorUsageElement16(self, ctx:SysMLv2Parser.RuleBehaviorUsageElement16Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement1.
    def visitRuleVariantUsageElement1(self, ctx:SysMLv2Parser.RuleVariantUsageElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement2.
    def visitRuleVariantUsageElement2(self, ctx:SysMLv2Parser.RuleVariantUsageElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement3.
    def visitRuleVariantUsageElement3(self, ctx:SysMLv2Parser.RuleVariantUsageElement3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement4.
    def visitRuleVariantUsageElement4(self, ctx:SysMLv2Parser.RuleVariantUsageElement4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement5.
    def visitRuleVariantUsageElement5(self, ctx:SysMLv2Parser.RuleVariantUsageElement5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement6.
    def visitRuleVariantUsageElement6(self, ctx:SysMLv2Parser.RuleVariantUsageElement6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement7.
    def visitRuleVariantUsageElement7(self, ctx:SysMLv2Parser.RuleVariantUsageElement7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement8.
    def visitRuleVariantUsageElement8(self, ctx:SysMLv2Parser.RuleVariantUsageElement8Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement9.
    def visitRuleVariantUsageElement9(self, ctx:SysMLv2Parser.RuleVariantUsageElement9Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement10.
    def visitRuleVariantUsageElement10(self, ctx:SysMLv2Parser.RuleVariantUsageElement10Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement11.
    def visitRuleVariantUsageElement11(self, ctx:SysMLv2Parser.RuleVariantUsageElement11Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement12.
    def visitRuleVariantUsageElement12(self, ctx:SysMLv2Parser.RuleVariantUsageElement12Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement13.
    def visitRuleVariantUsageElement13(self, ctx:SysMLv2Parser.RuleVariantUsageElement13Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement14.
    def visitRuleVariantUsageElement14(self, ctx:SysMLv2Parser.RuleVariantUsageElement14Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement15.
    def visitRuleVariantUsageElement15(self, ctx:SysMLv2Parser.RuleVariantUsageElement15Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement16.
    def visitRuleVariantUsageElement16(self, ctx:SysMLv2Parser.RuleVariantUsageElement16Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement17.
    def visitRuleVariantUsageElement17(self, ctx:SysMLv2Parser.RuleVariantUsageElement17Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement18.
    def visitRuleVariantUsageElement18(self, ctx:SysMLv2Parser.RuleVariantUsageElement18Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement19.
    def visitRuleVariantUsageElement19(self, ctx:SysMLv2Parser.RuleVariantUsageElement19Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement20.
    def visitRuleVariantUsageElement20(self, ctx:SysMLv2Parser.RuleVariantUsageElement20Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVariantUsageElement21.
    def visitRuleVariantUsageElement21(self, ctx:SysMLv2Parser.RuleVariantUsageElement21Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExtendedDefinition.
    def visitRuleExtendedDefinition(self, ctx:SysMLv2Parser.RuleExtendedDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExtendedUsage.
    def visitRuleExtendedUsage(self, ctx:SysMLv2Parser.RuleExtendedUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAttributeKeyword.
    def visitRuleAttributeKeyword(self, ctx:SysMLv2Parser.RuleAttributeKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAttributeDefKeyword.
    def visitRuleAttributeDefKeyword(self, ctx:SysMLv2Parser.RuleAttributeDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAttributeUsageKeyword.
    def visitRuleAttributeUsageKeyword(self, ctx:SysMLv2Parser.RuleAttributeUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAttributeDefinition.
    def visitRuleAttributeDefinition(self, ctx:SysMLv2Parser.RuleAttributeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAttributeUsage.
    def visitRuleAttributeUsage(self, ctx:SysMLv2Parser.RuleAttributeUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEnumerationKeyword.
    def visitRuleEnumerationKeyword(self, ctx:SysMLv2Parser.RuleEnumerationKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEnumerationDefKeyword.
    def visitRuleEnumerationDefKeyword(self, ctx:SysMLv2Parser.RuleEnumerationDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEnumerationUsageKeyword.
    def visitRuleEnumerationUsageKeyword(self, ctx:SysMLv2Parser.RuleEnumerationUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEnumerationDefinition.
    def visitRuleEnumerationDefinition(self, ctx:SysMLv2Parser.RuleEnumerationDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEnumerationBody1.
    def visitRuleEnumerationBody1(self, ctx:SysMLv2Parser.RuleEnumerationBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEnumerationBody2.
    def visitRuleEnumerationBody2(self, ctx:SysMLv2Parser.RuleEnumerationBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEnumerationUsageMember.
    def visitRuleEnumerationUsageMember(self, ctx:SysMLv2Parser.RuleEnumerationUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEnumeratedValue.
    def visitRuleEnumeratedValue(self, ctx:SysMLv2Parser.RuleEnumeratedValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEnumerationUsage.
    def visitRuleEnumerationUsage(self, ctx:SysMLv2Parser.RuleEnumerationUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceKeyword.
    def visitRuleOccurrenceKeyword(self, ctx:SysMLv2Parser.RuleOccurrenceKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceDefKeyword.
    def visitRuleOccurrenceDefKeyword(self, ctx:SysMLv2Parser.RuleOccurrenceDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceDefinitionPrefix.
    def visitRuleOccurrenceDefinitionPrefix(self, ctx:SysMLv2Parser.RuleOccurrenceDefinitionPrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceDefinition.
    def visitRuleOccurrenceDefinition(self, ctx:SysMLv2Parser.RuleOccurrenceDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleIndividualDefinition.
    def visitRuleIndividualDefinition(self, ctx:SysMLv2Parser.RuleIndividualDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLifeClassMembership.
    def visitRuleLifeClassMembership(self, ctx:SysMLv2Parser.RuleLifeClassMembershipContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLifeClass.
    def visitRuleLifeClass(self, ctx:SysMLv2Parser.RuleLifeClassContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceUsageKeyword.
    def visitRuleOccurrenceUsageKeyword(self, ctx:SysMLv2Parser.RuleOccurrenceUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceUsagePrefix.
    def visitRuleOccurrenceUsagePrefix(self, ctx:SysMLv2Parser.RuleOccurrenceUsagePrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOccurrenceUsage.
    def visitRuleOccurrenceUsage(self, ctx:SysMLv2Parser.RuleOccurrenceUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleIndividualUsage.
    def visitRuleIndividualUsage(self, ctx:SysMLv2Parser.RuleIndividualUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePortionUsage.
    def visitRulePortionUsage(self, ctx:SysMLv2Parser.RulePortionUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEventOccurrenceUsage.
    def visitRuleEventOccurrenceUsage(self, ctx:SysMLv2Parser.RuleEventOccurrenceUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptySuccessionMember.
    def visitRuleEmptySuccessionMember(self, ctx:SysMLv2Parser.RuleEmptySuccessionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptySuccession.
    def visitRuleEmptySuccession(self, ctx:SysMLv2Parser.RuleEmptySuccessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicitySourceEndMember.
    def visitRuleMultiplicitySourceEndMember(self, ctx:SysMLv2Parser.RuleMultiplicitySourceEndMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicitySourceEnd.
    def visitRuleMultiplicitySourceEnd(self, ctx:SysMLv2Parser.RuleMultiplicitySourceEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptyTargetEndMember.
    def visitRuleEmptyTargetEndMember(self, ctx:SysMLv2Parser.RuleEmptyTargetEndMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptyTargetEnd.
    def visitRuleEmptyTargetEnd(self, ctx:SysMLv2Parser.RuleEmptyTargetEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleItemKeyword.
    def visitRuleItemKeyword(self, ctx:SysMLv2Parser.RuleItemKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleItemDefKeyword.
    def visitRuleItemDefKeyword(self, ctx:SysMLv2Parser.RuleItemDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleItemUsageKeyword.
    def visitRuleItemUsageKeyword(self, ctx:SysMLv2Parser.RuleItemUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleItemDefinition.
    def visitRuleItemDefinition(self, ctx:SysMLv2Parser.RuleItemDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleItemUsage.
    def visitRuleItemUsage(self, ctx:SysMLv2Parser.RuleItemUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePartKeyword.
    def visitRulePartKeyword(self, ctx:SysMLv2Parser.RulePartKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePartDefKeyword.
    def visitRulePartDefKeyword(self, ctx:SysMLv2Parser.RulePartDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePartUsageKeyword.
    def visitRulePartUsageKeyword(self, ctx:SysMLv2Parser.RulePartUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePartDefinition.
    def visitRulePartDefinition(self, ctx:SysMLv2Parser.RulePartDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePartUsage.
    def visitRulePartUsage(self, ctx:SysMLv2Parser.RulePartUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePortKeyword.
    def visitRulePortKeyword(self, ctx:SysMLv2Parser.RulePortKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePortDefKeyword.
    def visitRulePortDefKeyword(self, ctx:SysMLv2Parser.RulePortDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePortDefinition.
    def visitRulePortDefinition(self, ctx:SysMLv2Parser.RulePortDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConjugatedPortDefinitionMember.
    def visitRuleConjugatedPortDefinitionMember(self, ctx:SysMLv2Parser.RuleConjugatedPortDefinitionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConjugatedPortDefinition.
    def visitRuleConjugatedPortDefinition(self, ctx:SysMLv2Parser.RuleConjugatedPortDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePortConjugation.
    def visitRulePortConjugation(self, ctx:SysMLv2Parser.RulePortConjugationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConjugatedPortTyping.
    def visitRuleConjugatedPortTyping(self, ctx:SysMLv2Parser.RuleConjugatedPortTypingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConjugatedQualifiedName.
    def visitRuleConjugatedQualifiedName(self, ctx:SysMLv2Parser.RuleConjugatedQualifiedNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePortUsageKeyword.
    def visitRulePortUsageKeyword(self, ctx:SysMLv2Parser.RulePortUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePortUsage.
    def visitRulePortUsage(self, ctx:SysMLv2Parser.RulePortUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectorEndMember.
    def visitRuleConnectorEndMember(self, ctx:SysMLv2Parser.RuleConnectorEndMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectorEnd.
    def visitRuleConnectorEnd(self, ctx:SysMLv2Parser.RuleConnectorEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedCrossMultiplicityMember.
    def visitRuleOwnedCrossMultiplicityMember(self, ctx:SysMLv2Parser.RuleOwnedCrossMultiplicityMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedCrossMultiplicity.
    def visitRuleOwnedCrossMultiplicity(self, ctx:SysMLv2Parser.RuleOwnedCrossMultiplicityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBindingKeyword.
    def visitRuleBindingKeyword(self, ctx:SysMLv2Parser.RuleBindingKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBindingConnectorAsUsage.
    def visitRuleBindingConnectorAsUsage(self, ctx:SysMLv2Parser.RuleBindingConnectorAsUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSuccessionKeyword.
    def visitRuleSuccessionKeyword(self, ctx:SysMLv2Parser.RuleSuccessionKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSuccessionAsUsage.
    def visitRuleSuccessionAsUsage(self, ctx:SysMLv2Parser.RuleSuccessionAsUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectionKeyword.
    def visitRuleConnectionKeyword(self, ctx:SysMLv2Parser.RuleConnectionKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectionDefKeyword.
    def visitRuleConnectionDefKeyword(self, ctx:SysMLv2Parser.RuleConnectionDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectionDefinition.
    def visitRuleConnectionDefinition(self, ctx:SysMLv2Parser.RuleConnectionDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectorKeyword.
    def visitRuleConnectorKeyword(self, ctx:SysMLv2Parser.RuleConnectorKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectionUsageKeyword.
    def visitRuleConnectionUsageKeyword(self, ctx:SysMLv2Parser.RuleConnectionUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectionUsage.
    def visitRuleConnectionUsage(self, ctx:SysMLv2Parser.RuleConnectionUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectorPart1.
    def visitRuleConnectorPart1(self, ctx:SysMLv2Parser.RuleConnectorPart1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConnectorPart2.
    def visitRuleConnectorPart2(self, ctx:SysMLv2Parser.RuleConnectorPart2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBinaryConnectorPart.
    def visitRuleBinaryConnectorPart(self, ctx:SysMLv2Parser.RuleBinaryConnectorPartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNaryConnectorPart.
    def visitRuleNaryConnectorPart(self, ctx:SysMLv2Parser.RuleNaryConnectorPartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptySourceEndMember.
    def visitRuleEmptySourceEndMember(self, ctx:SysMLv2Parser.RuleEmptySourceEndMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptySourceEnd.
    def visitRuleEmptySourceEnd(self, ctx:SysMLv2Parser.RuleEmptySourceEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceKeyword.
    def visitRuleInterfaceKeyword(self, ctx:SysMLv2Parser.RuleInterfaceKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceDefKeyword.
    def visitRuleInterfaceDefKeyword(self, ctx:SysMLv2Parser.RuleInterfaceDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceDefinition.
    def visitRuleInterfaceDefinition(self, ctx:SysMLv2Parser.RuleInterfaceDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceBody1.
    def visitRuleInterfaceBody1(self, ctx:SysMLv2Parser.RuleInterfaceBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceBody2.
    def visitRuleInterfaceBody2(self, ctx:SysMLv2Parser.RuleInterfaceBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceBodyItem1.
    def visitRuleInterfaceBodyItem1(self, ctx:SysMLv2Parser.RuleInterfaceBodyItem1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceBodyItem2.
    def visitRuleInterfaceBodyItem2(self, ctx:SysMLv2Parser.RuleInterfaceBodyItem2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceBodyItem3.
    def visitRuleInterfaceBodyItem3(self, ctx:SysMLv2Parser.RuleInterfaceBodyItem3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceBodyItem4.
    def visitRuleInterfaceBodyItem4(self, ctx:SysMLv2Parser.RuleInterfaceBodyItem4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceBodyItem5.
    def visitRuleInterfaceBodyItem5(self, ctx:SysMLv2Parser.RuleInterfaceBodyItem5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceBodyItem6.
    def visitRuleInterfaceBodyItem6(self, ctx:SysMLv2Parser.RuleInterfaceBodyItem6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceNonOccurrenceUsageMember.
    def visitRuleInterfaceNonOccurrenceUsageMember(self, ctx:SysMLv2Parser.RuleInterfaceNonOccurrenceUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceNonOccurrenceUsageElement1.
    def visitRuleInterfaceNonOccurrenceUsageElement1(self, ctx:SysMLv2Parser.RuleInterfaceNonOccurrenceUsageElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceNonOccurrenceUsageElement2.
    def visitRuleInterfaceNonOccurrenceUsageElement2(self, ctx:SysMLv2Parser.RuleInterfaceNonOccurrenceUsageElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceNonOccurrenceUsageElement3.
    def visitRuleInterfaceNonOccurrenceUsageElement3(self, ctx:SysMLv2Parser.RuleInterfaceNonOccurrenceUsageElement3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceNonOccurrenceUsageElement4.
    def visitRuleInterfaceNonOccurrenceUsageElement4(self, ctx:SysMLv2Parser.RuleInterfaceNonOccurrenceUsageElement4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceNonOccurrenceUsageElement5.
    def visitRuleInterfaceNonOccurrenceUsageElement5(self, ctx:SysMLv2Parser.RuleInterfaceNonOccurrenceUsageElement5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceOccurrenceUsageMember.
    def visitRuleInterfaceOccurrenceUsageMember(self, ctx:SysMLv2Parser.RuleInterfaceOccurrenceUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceOccurrenceUsageElement1.
    def visitRuleInterfaceOccurrenceUsageElement1(self, ctx:SysMLv2Parser.RuleInterfaceOccurrenceUsageElement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceOccurrenceUsageElement2.
    def visitRuleInterfaceOccurrenceUsageElement2(self, ctx:SysMLv2Parser.RuleInterfaceOccurrenceUsageElement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceOccurrenceUsageElement3.
    def visitRuleInterfaceOccurrenceUsageElement3(self, ctx:SysMLv2Parser.RuleInterfaceOccurrenceUsageElement3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefaultInterfaceEnd.
    def visitRuleDefaultInterfaceEnd(self, ctx:SysMLv2Parser.RuleDefaultInterfaceEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceUsageKeyword.
    def visitRuleInterfaceUsageKeyword(self, ctx:SysMLv2Parser.RuleInterfaceUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceUsage.
    def visitRuleInterfaceUsage(self, ctx:SysMLv2Parser.RuleInterfaceUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceUsageDeclaration1.
    def visitRuleInterfaceUsageDeclaration1(self, ctx:SysMLv2Parser.RuleInterfaceUsageDeclaration1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceUsageDeclaration2.
    def visitRuleInterfaceUsageDeclaration2(self, ctx:SysMLv2Parser.RuleInterfaceUsageDeclaration2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfacePart1.
    def visitRuleInterfacePart1(self, ctx:SysMLv2Parser.RuleInterfacePart1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfacePart2.
    def visitRuleInterfacePart2(self, ctx:SysMLv2Parser.RuleInterfacePart2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBinaryInterfacePart.
    def visitRuleBinaryInterfacePart(self, ctx:SysMLv2Parser.RuleBinaryInterfacePartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNaryInterfacePart.
    def visitRuleNaryInterfacePart(self, ctx:SysMLv2Parser.RuleNaryInterfacePartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceEndMember.
    def visitRuleInterfaceEndMember(self, ctx:SysMLv2Parser.RuleInterfaceEndMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInterfaceEnd.
    def visitRuleInterfaceEnd(self, ctx:SysMLv2Parser.RuleInterfaceEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAllocationKeyword.
    def visitRuleAllocationKeyword(self, ctx:SysMLv2Parser.RuleAllocationKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAllocationDefKeyword.
    def visitRuleAllocationDefKeyword(self, ctx:SysMLv2Parser.RuleAllocationDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAllocationDefinition.
    def visitRuleAllocationDefinition(self, ctx:SysMLv2Parser.RuleAllocationDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAllocationUsageKeyword.
    def visitRuleAllocationUsageKeyword(self, ctx:SysMLv2Parser.RuleAllocationUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAllocateKeyword.
    def visitRuleAllocateKeyword(self, ctx:SysMLv2Parser.RuleAllocateKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAllocationUsage.
    def visitRuleAllocationUsage(self, ctx:SysMLv2Parser.RuleAllocationUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAllocationUsageDeclaration1.
    def visitRuleAllocationUsageDeclaration1(self, ctx:SysMLv2Parser.RuleAllocationUsageDeclaration1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAllocationUsageDeclaration2.
    def visitRuleAllocationUsageDeclaration2(self, ctx:SysMLv2Parser.RuleAllocationUsageDeclaration2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowConnectionKeyword.
    def visitRuleFlowConnectionKeyword(self, ctx:SysMLv2Parser.RuleFlowConnectionKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowConnectionDefKeyword.
    def visitRuleFlowConnectionDefKeyword(self, ctx:SysMLv2Parser.RuleFlowConnectionDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowConnectionDefinition.
    def visitRuleFlowConnectionDefinition(self, ctx:SysMLv2Parser.RuleFlowConnectionDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMessageKeyword.
    def visitRuleMessageKeyword(self, ctx:SysMLv2Parser.RuleMessageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMessage.
    def visitRuleMessage(self, ctx:SysMLv2Parser.RuleMessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMessageDeclaration1.
    def visitRuleMessageDeclaration1(self, ctx:SysMLv2Parser.RuleMessageDeclaration1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMessageDeclaration2.
    def visitRuleMessageDeclaration2(self, ctx:SysMLv2Parser.RuleMessageDeclaration2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMessageEventMember.
    def visitRuleMessageEventMember(self, ctx:SysMLv2Parser.RuleMessageEventMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMessageEvent.
    def visitRuleMessageEvent(self, ctx:SysMLv2Parser.RuleMessageEventContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowConnectionUsage.
    def visitRuleFlowConnectionUsage(self, ctx:SysMLv2Parser.RuleFlowConnectionUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSuccessionFlowConnectionKeyword.
    def visitRuleSuccessionFlowConnectionKeyword(self, ctx:SysMLv2Parser.RuleSuccessionFlowConnectionKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSuccessionFlowConnectionUsage.
    def visitRuleSuccessionFlowConnectionUsage(self, ctx:SysMLv2Parser.RuleSuccessionFlowConnectionUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowConnectionDeclaration1.
    def visitRuleFlowConnectionDeclaration1(self, ctx:SysMLv2Parser.RuleFlowConnectionDeclaration1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowConnectionDeclaration2.
    def visitRuleFlowConnectionDeclaration2(self, ctx:SysMLv2Parser.RuleFlowConnectionDeclaration2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleItemFeatureMember.
    def visitRuleItemFeatureMember(self, ctx:SysMLv2Parser.RuleItemFeatureMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleItemFeature.
    def visitRuleItemFeature(self, ctx:SysMLv2Parser.RuleItemFeatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePayloadFeature1.
    def visitRulePayloadFeature1(self, ctx:SysMLv2Parser.RulePayloadFeature1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePayloadFeature2.
    def visitRulePayloadFeature2(self, ctx:SysMLv2Parser.RulePayloadFeature2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePayloadFeature3.
    def visitRulePayloadFeature3(self, ctx:SysMLv2Parser.RulePayloadFeature3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePayloadFeature4.
    def visitRulePayloadFeature4(self, ctx:SysMLv2Parser.RulePayloadFeature4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePayloadFeatureSpecializationPart1.
    def visitRulePayloadFeatureSpecializationPart1(self, ctx:SysMLv2Parser.RulePayloadFeatureSpecializationPart1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePayloadFeatureSpecializationPart2.
    def visitRulePayloadFeatureSpecializationPart2(self, ctx:SysMLv2Parser.RulePayloadFeatureSpecializationPart2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowEndMember.
    def visitRuleFlowEndMember(self, ctx:SysMLv2Parser.RuleFlowEndMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowEnd.
    def visitRuleFlowEnd(self, ctx:SysMLv2Parser.RuleFlowEndContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowEndSubsetting1.
    def visitRuleFlowEndSubsetting1(self, ctx:SysMLv2Parser.RuleFlowEndSubsetting1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowEndSubsetting2.
    def visitRuleFlowEndSubsetting2(self, ctx:SysMLv2Parser.RuleFlowEndSubsetting2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureChainPrefix.
    def visitRuleFeatureChainPrefix(self, ctx:SysMLv2Parser.RuleFeatureChainPrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowFeatureMember.
    def visitRuleFlowFeatureMember(self, ctx:SysMLv2Parser.RuleFlowFeatureMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowFeature.
    def visitRuleFlowFeature(self, ctx:SysMLv2Parser.RuleFlowFeatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFlowRedefinition.
    def visitRuleFlowRedefinition(self, ctx:SysMLv2Parser.RuleFlowRedefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionKeyword.
    def visitRuleActionKeyword(self, ctx:SysMLv2Parser.RuleActionKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionDefKeyword.
    def visitRuleActionDefKeyword(self, ctx:SysMLv2Parser.RuleActionDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionDefinition.
    def visitRuleActionDefinition(self, ctx:SysMLv2Parser.RuleActionDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBody1.
    def visitRuleActionBody1(self, ctx:SysMLv2Parser.RuleActionBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBody2.
    def visitRuleActionBody2(self, ctx:SysMLv2Parser.RuleActionBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyItem1.
    def visitRuleActionBodyItem1(self, ctx:SysMLv2Parser.RuleActionBodyItem1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyItem2.
    def visitRuleActionBodyItem2(self, ctx:SysMLv2Parser.RuleActionBodyItem2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyItem3.
    def visitRuleActionBodyItem3(self, ctx:SysMLv2Parser.RuleActionBodyItem3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyItem4.
    def visitRuleActionBodyItem4(self, ctx:SysMLv2Parser.RuleActionBodyItem4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyItem5.
    def visitRuleActionBodyItem5(self, ctx:SysMLv2Parser.RuleActionBodyItem5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyItem6.
    def visitRuleActionBodyItem6(self, ctx:SysMLv2Parser.RuleActionBodyItem6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyItem7.
    def visitRuleActionBodyItem7(self, ctx:SysMLv2Parser.RuleActionBodyItem7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyItem8.
    def visitRuleActionBodyItem8(self, ctx:SysMLv2Parser.RuleActionBodyItem8Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyItem9.
    def visitRuleActionBodyItem9(self, ctx:SysMLv2Parser.RuleActionBodyItem9Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInitialNodeMember.
    def visitRuleInitialNodeMember(self, ctx:SysMLv2Parser.RuleInitialNodeMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNodeMember.
    def visitRuleActionNodeMember(self, ctx:SysMLv2Parser.RuleActionNodeMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetSuccessionMember.
    def visitRuleTargetSuccessionMember(self, ctx:SysMLv2Parser.RuleTargetSuccessionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleGuardedSuccessionMember.
    def visitRuleGuardedSuccessionMember(self, ctx:SysMLv2Parser.RuleGuardedSuccessionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionUsageKeyword.
    def visitRuleActionUsageKeyword(self, ctx:SysMLv2Parser.RuleActionUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionUsage.
    def visitRuleActionUsage(self, ctx:SysMLv2Parser.RuleActionUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePerformActionUsage.
    def visitRulePerformActionUsage(self, ctx:SysMLv2Parser.RulePerformActionUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePerformActionUsageDeclaration.
    def visitRulePerformActionUsageDeclaration(self, ctx:SysMLv2Parser.RulePerformActionUsageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionUsageDeclaration.
    def visitRuleActionUsageDeclaration(self, ctx:SysMLv2Parser.RuleActionUsageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNode1.
    def visitRuleActionNode1(self, ctx:SysMLv2Parser.RuleActionNode1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNode2.
    def visitRuleActionNode2(self, ctx:SysMLv2Parser.RuleActionNode2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNode3.
    def visitRuleActionNode3(self, ctx:SysMLv2Parser.RuleActionNode3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNode4.
    def visitRuleActionNode4(self, ctx:SysMLv2Parser.RuleActionNode4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNode5.
    def visitRuleActionNode5(self, ctx:SysMLv2Parser.RuleActionNode5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNode6.
    def visitRuleActionNode6(self, ctx:SysMLv2Parser.RuleActionNode6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNode7.
    def visitRuleActionNode7(self, ctx:SysMLv2Parser.RuleActionNode7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNode8.
    def visitRuleActionNode8(self, ctx:SysMLv2Parser.RuleActionNode8Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNodeUsageDeclaration.
    def visitRuleActionNodeUsageDeclaration(self, ctx:SysMLv2Parser.RuleActionNodeUsageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNodePrefix.
    def visitRuleActionNodePrefix(self, ctx:SysMLv2Parser.RuleActionNodePrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAcceptNode.
    def visitRuleAcceptNode(self, ctx:SysMLv2Parser.RuleAcceptNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAcceptNodeDeclaration.
    def visitRuleAcceptNodeDeclaration(self, ctx:SysMLv2Parser.RuleAcceptNodeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAcceptParameterPart.
    def visitRuleAcceptParameterPart(self, ctx:SysMLv2Parser.RuleAcceptParameterPartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePayloadParameterMember.
    def visitRulePayloadParameterMember(self, ctx:SysMLv2Parser.RulePayloadParameterMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePayloadParameter1.
    def visitRulePayloadParameter1(self, ctx:SysMLv2Parser.RulePayloadParameter1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePayloadParameter2.
    def visitRulePayloadParameter2(self, ctx:SysMLv2Parser.RulePayloadParameter2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTriggerValuePart.
    def visitRuleTriggerValuePart(self, ctx:SysMLv2Parser.RuleTriggerValuePartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTriggerFeatureValue.
    def visitRuleTriggerFeatureValue(self, ctx:SysMLv2Parser.RuleTriggerFeatureValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTriggerExpression1.
    def visitRuleTriggerExpression1(self, ctx:SysMLv2Parser.RuleTriggerExpression1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTriggerExpression2.
    def visitRuleTriggerExpression2(self, ctx:SysMLv2Parser.RuleTriggerExpression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTimeTriggerKind1.
    def visitRuleTimeTriggerKind1(self, ctx:SysMLv2Parser.RuleTimeTriggerKind1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTimeTriggerKind2.
    def visitRuleTimeTriggerKind2(self, ctx:SysMLv2Parser.RuleTimeTriggerKind2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleChangeTriggerKind.
    def visitRuleChangeTriggerKind(self, ctx:SysMLv2Parser.RuleChangeTriggerKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleArgumentExpressionMember.
    def visitRuleArgumentExpressionMember(self, ctx:SysMLv2Parser.RuleArgumentExpressionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleArgumentExpression.
    def visitRuleArgumentExpression(self, ctx:SysMLv2Parser.RuleArgumentExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleArgumentExpressionValue.
    def visitRuleArgumentExpressionValue(self, ctx:SysMLv2Parser.RuleArgumentExpressionValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSendNode.
    def visitRuleSendNode(self, ctx:SysMLv2Parser.RuleSendNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSendNodeDeclaration.
    def visitRuleSendNodeDeclaration(self, ctx:SysMLv2Parser.RuleSendNodeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNodeParameterMember.
    def visitRuleNodeParameterMember(self, ctx:SysMLv2Parser.RuleNodeParameterMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNodeParameter.
    def visitRuleNodeParameter(self, ctx:SysMLv2Parser.RuleNodeParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureBinding.
    def visitRuleFeatureBinding(self, ctx:SysMLv2Parser.RuleFeatureBindingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAssignmentNode.
    def visitRuleAssignmentNode(self, ctx:SysMLv2Parser.RuleAssignmentNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAssignmentNodeDeclaration.
    def visitRuleAssignmentNodeDeclaration(self, ctx:SysMLv2Parser.RuleAssignmentNodeDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAssignmentTargetMember.
    def visitRuleAssignmentTargetMember(self, ctx:SysMLv2Parser.RuleAssignmentTargetMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetParameter.
    def visitRuleTargetParameter(self, ctx:SysMLv2Parser.RuleTargetParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetFeatureMember.
    def visitRuleTargetFeatureMember(self, ctx:SysMLv2Parser.RuleTargetFeatureMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetFeature.
    def visitRuleTargetFeature(self, ctx:SysMLv2Parser.RuleTargetFeatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetAccessedFeatureMember.
    def visitRuleTargetAccessedFeatureMember(self, ctx:SysMLv2Parser.RuleTargetAccessedFeatureMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetBinding.
    def visitRuleTargetBinding(self, ctx:SysMLv2Parser.RuleTargetBindingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetExpression.
    def visitRuleTargetExpression(self, ctx:SysMLv2Parser.RuleTargetExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExpressionParameterMember.
    def visitRuleExpressionParameterMember(self, ctx:SysMLv2Parser.RuleExpressionParameterMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleIfNode.
    def visitRuleIfNode(self, ctx:SysMLv2Parser.RuleIfNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyParameterMember.
    def visitRuleActionBodyParameterMember(self, ctx:SysMLv2Parser.RuleActionBodyParameterMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionBodyParameter.
    def visitRuleActionBodyParameter(self, ctx:SysMLv2Parser.RuleActionBodyParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleIfNodeParameterMember.
    def visitRuleIfNodeParameterMember(self, ctx:SysMLv2Parser.RuleIfNodeParameterMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleWhileLoopNode.
    def visitRuleWhileLoopNode(self, ctx:SysMLv2Parser.RuleWhileLoopNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleForLoopNode.
    def visitRuleForLoopNode(self, ctx:SysMLv2Parser.RuleForLoopNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleForVariableDeclarationMember.
    def visitRuleForVariableDeclarationMember(self, ctx:SysMLv2Parser.RuleForVariableDeclarationMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleForVariableDeclaration.
    def visitRuleForVariableDeclaration(self, ctx:SysMLv2Parser.RuleForVariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTerminateNode.
    def visitRuleTerminateNode(self, ctx:SysMLv2Parser.RuleTerminateNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleControlNode1.
    def visitRuleControlNode1(self, ctx:SysMLv2Parser.RuleControlNode1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleControlNode2.
    def visitRuleControlNode2(self, ctx:SysMLv2Parser.RuleControlNode2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleControlNode3.
    def visitRuleControlNode3(self, ctx:SysMLv2Parser.RuleControlNode3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleControlNode4.
    def visitRuleControlNode4(self, ctx:SysMLv2Parser.RuleControlNode4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleControlNodePrefix.
    def visitRuleControlNodePrefix(self, ctx:SysMLv2Parser.RuleControlNodePrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMergeNode.
    def visitRuleMergeNode(self, ctx:SysMLv2Parser.RuleMergeNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDecisionNode.
    def visitRuleDecisionNode(self, ctx:SysMLv2Parser.RuleDecisionNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleJoinNode.
    def visitRuleJoinNode(self, ctx:SysMLv2Parser.RuleJoinNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleForkNode.
    def visitRuleForkNode(self, ctx:SysMLv2Parser.RuleForkNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNodeBody1.
    def visitRuleActionNodeBody1(self, ctx:SysMLv2Parser.RuleActionNodeBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionNodeBody2.
    def visitRuleActionNodeBody2(self, ctx:SysMLv2Parser.RuleActionNodeBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptyParameterMember.
    def visitRuleEmptyParameterMember(self, ctx:SysMLv2Parser.RuleEmptyParameterMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptyUsage.
    def visitRuleEmptyUsage(self, ctx:SysMLv2Parser.RuleEmptyUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActionTargetSuccession.
    def visitRuleActionTargetSuccession(self, ctx:SysMLv2Parser.RuleActionTargetSuccessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetSuccession.
    def visitRuleTargetSuccession(self, ctx:SysMLv2Parser.RuleTargetSuccessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleGuardedTargetSuccession.
    def visitRuleGuardedTargetSuccession(self, ctx:SysMLv2Parser.RuleGuardedTargetSuccessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDefaultTargetSuccession.
    def visitRuleDefaultTargetSuccession(self, ctx:SysMLv2Parser.RuleDefaultTargetSuccessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleGuardedSuccession.
    def visitRuleGuardedSuccession(self, ctx:SysMLv2Parser.RuleGuardedSuccessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateKeyword.
    def visitRuleStateKeyword(self, ctx:SysMLv2Parser.RuleStateKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateDefKeyword.
    def visitRuleStateDefKeyword(self, ctx:SysMLv2Parser.RuleStateDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateDefinition.
    def visitRuleStateDefinition(self, ctx:SysMLv2Parser.RuleStateDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateDefBody1.
    def visitRuleStateDefBody1(self, ctx:SysMLv2Parser.RuleStateDefBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateDefBody2.
    def visitRuleStateDefBody2(self, ctx:SysMLv2Parser.RuleStateDefBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyPart.
    def visitRuleStateBodyPart(self, ctx:SysMLv2Parser.RuleStateBodyPartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem1.
    def visitRuleStateBodyItem1(self, ctx:SysMLv2Parser.RuleStateBodyItem1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem2.
    def visitRuleStateBodyItem2(self, ctx:SysMLv2Parser.RuleStateBodyItem2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem3.
    def visitRuleStateBodyItem3(self, ctx:SysMLv2Parser.RuleStateBodyItem3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem4.
    def visitRuleStateBodyItem4(self, ctx:SysMLv2Parser.RuleStateBodyItem4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem5.
    def visitRuleStateBodyItem5(self, ctx:SysMLv2Parser.RuleStateBodyItem5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem6.
    def visitRuleStateBodyItem6(self, ctx:SysMLv2Parser.RuleStateBodyItem6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem7.
    def visitRuleStateBodyItem7(self, ctx:SysMLv2Parser.RuleStateBodyItem7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem8.
    def visitRuleStateBodyItem8(self, ctx:SysMLv2Parser.RuleStateBodyItem8Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem9.
    def visitRuleStateBodyItem9(self, ctx:SysMLv2Parser.RuleStateBodyItem9Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem10.
    def visitRuleStateBodyItem10(self, ctx:SysMLv2Parser.RuleStateBodyItem10Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateBodyItem11.
    def visitRuleStateBodyItem11(self, ctx:SysMLv2Parser.RuleStateBodyItem11Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEntryActionMember.
    def visitRuleEntryActionMember(self, ctx:SysMLv2Parser.RuleEntryActionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEntryActionKind.
    def visitRuleEntryActionKind(self, ctx:SysMLv2Parser.RuleEntryActionKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDoActionMember.
    def visitRuleDoActionMember(self, ctx:SysMLv2Parser.RuleDoActionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDoActionKind.
    def visitRuleDoActionKind(self, ctx:SysMLv2Parser.RuleDoActionKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExitActionMember.
    def visitRuleExitActionMember(self, ctx:SysMLv2Parser.RuleExitActionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExitActionKind.
    def visitRuleExitActionKind(self, ctx:SysMLv2Parser.RuleExitActionKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEntryTransitionMember.
    def visitRuleEntryTransitionMember(self, ctx:SysMLv2Parser.RuleEntryTransitionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateActionUsage1.
    def visitRuleStateActionUsage1(self, ctx:SysMLv2Parser.RuleStateActionUsage1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateActionUsage2.
    def visitRuleStateActionUsage2(self, ctx:SysMLv2Parser.RuleStateActionUsage2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptyActionUsage.
    def visitRuleEmptyActionUsage(self, ctx:SysMLv2Parser.RuleEmptyActionUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePerformedActionUsage1.
    def visitRulePerformedActionUsage1(self, ctx:SysMLv2Parser.RulePerformedActionUsage1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePerformedActionUsage2.
    def visitRulePerformedActionUsage2(self, ctx:SysMLv2Parser.RulePerformedActionUsage2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePerformedActionUsage3.
    def visitRulePerformedActionUsage3(self, ctx:SysMLv2Parser.RulePerformedActionUsage3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePerformedActionUsage4.
    def visitRulePerformedActionUsage4(self, ctx:SysMLv2Parser.RulePerformedActionUsage4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTransitionUsageMember.
    def visitRuleTransitionUsageMember(self, ctx:SysMLv2Parser.RuleTransitionUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetTransitionUsageMember.
    def visitRuleTargetTransitionUsageMember(self, ctx:SysMLv2Parser.RuleTargetTransitionUsageMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateUsageKeyword.
    def visitRuleStateUsageKeyword(self, ctx:SysMLv2Parser.RuleStateUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateUsage.
    def visitRuleStateUsage(self, ctx:SysMLv2Parser.RuleStateUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateUsageBody1.
    def visitRuleStateUsageBody1(self, ctx:SysMLv2Parser.RuleStateUsageBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateUsageBody2.
    def visitRuleStateUsageBody2(self, ctx:SysMLv2Parser.RuleStateUsageBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExhibitStateUsage.
    def visitRuleExhibitStateUsage(self, ctx:SysMLv2Parser.RuleExhibitStateUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTransitionUsageKeyword.
    def visitRuleTransitionUsageKeyword(self, ctx:SysMLv2Parser.RuleTransitionUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTransitionUsage.
    def visitRuleTransitionUsage(self, ctx:SysMLv2Parser.RuleTransitionUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTargetTransitionUsage.
    def visitRuleTargetTransitionUsage(self, ctx:SysMLv2Parser.RuleTargetTransitionUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTransitionSourceMember1.
    def visitRuleTransitionSourceMember1(self, ctx:SysMLv2Parser.RuleTransitionSourceMember1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTransitionSourceMember2.
    def visitRuleTransitionSourceMember2(self, ctx:SysMLv2Parser.RuleTransitionSourceMember2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTriggerActionMember.
    def visitRuleTriggerActionMember(self, ctx:SysMLv2Parser.RuleTriggerActionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTriggerAction.
    def visitRuleTriggerAction(self, ctx:SysMLv2Parser.RuleTriggerActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleGuardExpressionMember.
    def visitRuleGuardExpressionMember(self, ctx:SysMLv2Parser.RuleGuardExpressionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEffectBehaviorMember.
    def visitRuleEffectBehaviorMember(self, ctx:SysMLv2Parser.RuleEffectBehaviorMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEffectBehaviorUsage1.
    def visitRuleEffectBehaviorUsage1(self, ctx:SysMLv2Parser.RuleEffectBehaviorUsage1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEffectBehaviorUsage2.
    def visitRuleEffectBehaviorUsage2(self, ctx:SysMLv2Parser.RuleEffectBehaviorUsage2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTransitionSuccessionMember.
    def visitRuleTransitionSuccessionMember(self, ctx:SysMLv2Parser.RuleTransitionSuccessionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTransitionSuccession.
    def visitRuleTransitionSuccession(self, ctx:SysMLv2Parser.RuleTransitionSuccessionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationKeyword.
    def visitRuleCalculationKeyword(self, ctx:SysMLv2Parser.RuleCalculationKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationDefKeyword.
    def visitRuleCalculationDefKeyword(self, ctx:SysMLv2Parser.RuleCalculationDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationDefinition.
    def visitRuleCalculationDefinition(self, ctx:SysMLv2Parser.RuleCalculationDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationBody1.
    def visitRuleCalculationBody1(self, ctx:SysMLv2Parser.RuleCalculationBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationBody2.
    def visitRuleCalculationBody2(self, ctx:SysMLv2Parser.RuleCalculationBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationBodyPart.
    def visitRuleCalculationBodyPart(self, ctx:SysMLv2Parser.RuleCalculationBodyPartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationBodyItem1.
    def visitRuleCalculationBodyItem1(self, ctx:SysMLv2Parser.RuleCalculationBodyItem1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationBodyItem2.
    def visitRuleCalculationBodyItem2(self, ctx:SysMLv2Parser.RuleCalculationBodyItem2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleReturnParameterMember.
    def visitRuleReturnParameterMember(self, ctx:SysMLv2Parser.RuleReturnParameterMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleResultExpressionMember.
    def visitRuleResultExpressionMember(self, ctx:SysMLv2Parser.RuleResultExpressionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationUsageKeyword.
    def visitRuleCalculationUsageKeyword(self, ctx:SysMLv2Parser.RuleCalculationUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCalculationUsage.
    def visitRuleCalculationUsage(self, ctx:SysMLv2Parser.RuleCalculationUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConstraintKeyword.
    def visitRuleConstraintKeyword(self, ctx:SysMLv2Parser.RuleConstraintKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConstraintDefKeyword.
    def visitRuleConstraintDefKeyword(self, ctx:SysMLv2Parser.RuleConstraintDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConstraintDefinition.
    def visitRuleConstraintDefinition(self, ctx:SysMLv2Parser.RuleConstraintDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConstraintUsageKeyword.
    def visitRuleConstraintUsageKeyword(self, ctx:SysMLv2Parser.RuleConstraintUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConstraintUsage.
    def visitRuleConstraintUsage(self, ctx:SysMLv2Parser.RuleConstraintUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAssertConstraintUsage.
    def visitRuleAssertConstraintUsage(self, ctx:SysMLv2Parser.RuleAssertConstraintUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConstraintUsageDeclaration.
    def visitRuleConstraintUsageDeclaration(self, ctx:SysMLv2Parser.RuleConstraintUsageDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementKeyword.
    def visitRuleRequirementKeyword(self, ctx:SysMLv2Parser.RuleRequirementKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementDefKeyword.
    def visitRuleRequirementDefKeyword(self, ctx:SysMLv2Parser.RuleRequirementDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementDefinition.
    def visitRuleRequirementDefinition(self, ctx:SysMLv2Parser.RuleRequirementDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementBody1.
    def visitRuleRequirementBody1(self, ctx:SysMLv2Parser.RuleRequirementBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementBody2.
    def visitRuleRequirementBody2(self, ctx:SysMLv2Parser.RuleRequirementBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementBodyItem1.
    def visitRuleRequirementBodyItem1(self, ctx:SysMLv2Parser.RuleRequirementBodyItem1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementBodyItem2.
    def visitRuleRequirementBodyItem2(self, ctx:SysMLv2Parser.RuleRequirementBodyItem2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementBodyItem3.
    def visitRuleRequirementBodyItem3(self, ctx:SysMLv2Parser.RuleRequirementBodyItem3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementBodyItem4.
    def visitRuleRequirementBodyItem4(self, ctx:SysMLv2Parser.RuleRequirementBodyItem4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementBodyItem5.
    def visitRuleRequirementBodyItem5(self, ctx:SysMLv2Parser.RuleRequirementBodyItem5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementBodyItem6.
    def visitRuleRequirementBodyItem6(self, ctx:SysMLv2Parser.RuleRequirementBodyItem6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementBodyItem7.
    def visitRuleRequirementBodyItem7(self, ctx:SysMLv2Parser.RuleRequirementBodyItem7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSubjectMember.
    def visitRuleSubjectMember(self, ctx:SysMLv2Parser.RuleSubjectMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSubjectUsage.
    def visitRuleSubjectUsage(self, ctx:SysMLv2Parser.RuleSubjectUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementConstraintMember.
    def visitRuleRequirementConstraintMember(self, ctx:SysMLv2Parser.RuleRequirementConstraintMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementConstraintUsage1.
    def visitRuleRequirementConstraintUsage1(self, ctx:SysMLv2Parser.RuleRequirementConstraintUsage1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementConstraintUsage2.
    def visitRuleRequirementConstraintUsage2(self, ctx:SysMLv2Parser.RuleRequirementConstraintUsage2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFramedConcernMember.
    def visitRuleFramedConcernMember(self, ctx:SysMLv2Parser.RuleFramedConcernMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFramedConcernUsage1.
    def visitRuleFramedConcernUsage1(self, ctx:SysMLv2Parser.RuleFramedConcernUsage1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFramedConcernUsage2.
    def visitRuleFramedConcernUsage2(self, ctx:SysMLv2Parser.RuleFramedConcernUsage2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActorMember.
    def visitRuleActorMember(self, ctx:SysMLv2Parser.RuleActorMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleActorUsage.
    def visitRuleActorUsage(self, ctx:SysMLv2Parser.RuleActorUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStakeholderMember.
    def visitRuleStakeholderMember(self, ctx:SysMLv2Parser.RuleStakeholderMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStakeholderUsage.
    def visitRuleStakeholderUsage(self, ctx:SysMLv2Parser.RuleStakeholderUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementUsageKeyword.
    def visitRuleRequirementUsageKeyword(self, ctx:SysMLv2Parser.RuleRequirementUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementUsage.
    def visitRuleRequirementUsage(self, ctx:SysMLv2Parser.RuleRequirementUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSatisfyRequirementUsage.
    def visitRuleSatisfyRequirementUsage(self, ctx:SysMLv2Parser.RuleSatisfyRequirementUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSatisfactionSubjectMember.
    def visitRuleSatisfactionSubjectMember(self, ctx:SysMLv2Parser.RuleSatisfactionSubjectMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSatisfactionParameter.
    def visitRuleSatisfactionParameter(self, ctx:SysMLv2Parser.RuleSatisfactionParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSatisfactionFeatureValue.
    def visitRuleSatisfactionFeatureValue(self, ctx:SysMLv2Parser.RuleSatisfactionFeatureValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSatisfactionReferenceExpression.
    def visitRuleSatisfactionReferenceExpression(self, ctx:SysMLv2Parser.RuleSatisfactionReferenceExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConcernKeyword.
    def visitRuleConcernKeyword(self, ctx:SysMLv2Parser.RuleConcernKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConcernDefKeyword.
    def visitRuleConcernDefKeyword(self, ctx:SysMLv2Parser.RuleConcernDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConcernDefinition.
    def visitRuleConcernDefinition(self, ctx:SysMLv2Parser.RuleConcernDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConcernUsageKeyword.
    def visitRuleConcernUsageKeyword(self, ctx:SysMLv2Parser.RuleConcernUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConcernUsage.
    def visitRuleConcernUsage(self, ctx:SysMLv2Parser.RuleConcernUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseKeyword.
    def visitRuleCaseKeyword(self, ctx:SysMLv2Parser.RuleCaseKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseDefKeyword.
    def visitRuleCaseDefKeyword(self, ctx:SysMLv2Parser.RuleCaseDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseDefinition.
    def visitRuleCaseDefinition(self, ctx:SysMLv2Parser.RuleCaseDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseBody1.
    def visitRuleCaseBody1(self, ctx:SysMLv2Parser.RuleCaseBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseBody2.
    def visitRuleCaseBody2(self, ctx:SysMLv2Parser.RuleCaseBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseBodyItem1.
    def visitRuleCaseBodyItem1(self, ctx:SysMLv2Parser.RuleCaseBodyItem1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseBodyItem2.
    def visitRuleCaseBodyItem2(self, ctx:SysMLv2Parser.RuleCaseBodyItem2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseBodyItem3.
    def visitRuleCaseBodyItem3(self, ctx:SysMLv2Parser.RuleCaseBodyItem3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseBodyItem4.
    def visitRuleCaseBodyItem4(self, ctx:SysMLv2Parser.RuleCaseBodyItem4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleObjectiveMember.
    def visitRuleObjectiveMember(self, ctx:SysMLv2Parser.RuleObjectiveMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleObjectiveRequirementUsage.
    def visitRuleObjectiveRequirementUsage(self, ctx:SysMLv2Parser.RuleObjectiveRequirementUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseUsageKeyword.
    def visitRuleCaseUsageKeyword(self, ctx:SysMLv2Parser.RuleCaseUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseUsage.
    def visitRuleCaseUsage(self, ctx:SysMLv2Parser.RuleCaseUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnalysisCaseKeyword.
    def visitRuleAnalysisCaseKeyword(self, ctx:SysMLv2Parser.RuleAnalysisCaseKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnalysisCaseDefKeyword.
    def visitRuleAnalysisCaseDefKeyword(self, ctx:SysMLv2Parser.RuleAnalysisCaseDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnalysisCaseUsageKeyword.
    def visitRuleAnalysisCaseUsageKeyword(self, ctx:SysMLv2Parser.RuleAnalysisCaseUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnalysisCaseDefinition.
    def visitRuleAnalysisCaseDefinition(self, ctx:SysMLv2Parser.RuleAnalysisCaseDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnalysisCaseUsage.
    def visitRuleAnalysisCaseUsage(self, ctx:SysMLv2Parser.RuleAnalysisCaseUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVerificationCaseKeyword.
    def visitRuleVerificationCaseKeyword(self, ctx:SysMLv2Parser.RuleVerificationCaseKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVerificationCaseDefKeyword.
    def visitRuleVerificationCaseDefKeyword(self, ctx:SysMLv2Parser.RuleVerificationCaseDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVerificationCaseUsageKeyword.
    def visitRuleVerificationCaseUsageKeyword(self, ctx:SysMLv2Parser.RuleVerificationCaseUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVerificationCaseDefinition.
    def visitRuleVerificationCaseDefinition(self, ctx:SysMLv2Parser.RuleVerificationCaseDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVerificationCaseUsage.
    def visitRuleVerificationCaseUsage(self, ctx:SysMLv2Parser.RuleVerificationCaseUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementVerificationMember.
    def visitRuleRequirementVerificationMember(self, ctx:SysMLv2Parser.RuleRequirementVerificationMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementVerificationUsage1.
    def visitRuleRequirementVerificationUsage1(self, ctx:SysMLv2Parser.RuleRequirementVerificationUsage1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementVerificationUsage2.
    def visitRuleRequirementVerificationUsage2(self, ctx:SysMLv2Parser.RuleRequirementVerificationUsage2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUseCaseKeyword.
    def visitRuleUseCaseKeyword(self, ctx:SysMLv2Parser.RuleUseCaseKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUseCaseDefKeyword.
    def visitRuleUseCaseDefKeyword(self, ctx:SysMLv2Parser.RuleUseCaseDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUseCaseUsageKeyword.
    def visitRuleUseCaseUsageKeyword(self, ctx:SysMLv2Parser.RuleUseCaseUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUseCaseDefinition.
    def visitRuleUseCaseDefinition(self, ctx:SysMLv2Parser.RuleUseCaseDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUseCaseUsage.
    def visitRuleUseCaseUsage(self, ctx:SysMLv2Parser.RuleUseCaseUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleIncludeUseCaseUsage.
    def visitRuleIncludeUseCaseUsage(self, ctx:SysMLv2Parser.RuleIncludeUseCaseUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewKeyword.
    def visitRuleViewKeyword(self, ctx:SysMLv2Parser.RuleViewKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewDefKeyword.
    def visitRuleViewDefKeyword(self, ctx:SysMLv2Parser.RuleViewDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewDefinition.
    def visitRuleViewDefinition(self, ctx:SysMLv2Parser.RuleViewDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewDefinitionBody1.
    def visitRuleViewDefinitionBody1(self, ctx:SysMLv2Parser.RuleViewDefinitionBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewDefinitionBody2.
    def visitRuleViewDefinitionBody2(self, ctx:SysMLv2Parser.RuleViewDefinitionBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewDefinitionBodyItem1.
    def visitRuleViewDefinitionBodyItem1(self, ctx:SysMLv2Parser.RuleViewDefinitionBodyItem1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewDefinitionBodyItem2.
    def visitRuleViewDefinitionBodyItem2(self, ctx:SysMLv2Parser.RuleViewDefinitionBodyItem2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewDefinitionBodyItem3.
    def visitRuleViewDefinitionBodyItem3(self, ctx:SysMLv2Parser.RuleViewDefinitionBodyItem3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewRenderingMember.
    def visitRuleViewRenderingMember(self, ctx:SysMLv2Parser.RuleViewRenderingMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewRenderingUsage1.
    def visitRuleViewRenderingUsage1(self, ctx:SysMLv2Parser.RuleViewRenderingUsage1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewRenderingUsage2.
    def visitRuleViewRenderingUsage2(self, ctx:SysMLv2Parser.RuleViewRenderingUsage2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewUsageKeyword.
    def visitRuleViewUsageKeyword(self, ctx:SysMLv2Parser.RuleViewUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewUsage.
    def visitRuleViewUsage(self, ctx:SysMLv2Parser.RuleViewUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewBody1.
    def visitRuleViewBody1(self, ctx:SysMLv2Parser.RuleViewBody1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewBody2.
    def visitRuleViewBody2(self, ctx:SysMLv2Parser.RuleViewBody2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewBodyItem1.
    def visitRuleViewBodyItem1(self, ctx:SysMLv2Parser.RuleViewBodyItem1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewBodyItem2.
    def visitRuleViewBodyItem2(self, ctx:SysMLv2Parser.RuleViewBodyItem2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewBodyItem3.
    def visitRuleViewBodyItem3(self, ctx:SysMLv2Parser.RuleViewBodyItem3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewBodyItem4.
    def visitRuleViewBodyItem4(self, ctx:SysMLv2Parser.RuleViewBodyItem4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExposePrefix.
    def visitRuleExposePrefix(self, ctx:SysMLv2Parser.RuleExposePrefixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExpose.
    def visitRuleExpose(self, ctx:SysMLv2Parser.RuleExposeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMembershipExpose.
    def visitRuleMembershipExpose(self, ctx:SysMLv2Parser.RuleMembershipExposeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNamespaceExpose.
    def visitRuleNamespaceExpose(self, ctx:SysMLv2Parser.RuleNamespaceExposeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewpointKeyword.
    def visitRuleViewpointKeyword(self, ctx:SysMLv2Parser.RuleViewpointKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewpointDefKeyword.
    def visitRuleViewpointDefKeyword(self, ctx:SysMLv2Parser.RuleViewpointDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewpointUsageKeyword.
    def visitRuleViewpointUsageKeyword(self, ctx:SysMLv2Parser.RuleViewpointUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewpointDefinition.
    def visitRuleViewpointDefinition(self, ctx:SysMLv2Parser.RuleViewpointDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleViewpointUsage.
    def visitRuleViewpointUsage(self, ctx:SysMLv2Parser.RuleViewpointUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRenderingKeyword.
    def visitRuleRenderingKeyword(self, ctx:SysMLv2Parser.RuleRenderingKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRenderingDefKeyword.
    def visitRuleRenderingDefKeyword(self, ctx:SysMLv2Parser.RuleRenderingDefKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRenderingDefinition.
    def visitRuleRenderingDefinition(self, ctx:SysMLv2Parser.RuleRenderingDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRenderingUsageKeyword.
    def visitRuleRenderingUsageKeyword(self, ctx:SysMLv2Parser.RuleRenderingUsageKeywordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRenderingUsage.
    def visitRuleRenderingUsage(self, ctx:SysMLv2Parser.RuleRenderingUsageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExpressionBody.
    def visitRuleExpressionBody(self, ctx:SysMLv2Parser.RuleExpressionBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedExpressionMember.
    def visitRuleOwnedExpressionMember(self, ctx:SysMLv2Parser.RuleOwnedExpressionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedExpression.
    def visitRuleOwnedExpression(self, ctx:SysMLv2Parser.RuleOwnedExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedExpressionReference.
    def visitRuleOwnedExpressionReference(self, ctx:SysMLv2Parser.RuleOwnedExpressionReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConditionalExpression1.
    def visitRuleConditionalExpression1(self, ctx:SysMLv2Parser.RuleConditionalExpression1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConditionalExpression2.
    def visitRuleConditionalExpression2(self, ctx:SysMLv2Parser.RuleConditionalExpression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConditionalOperator.
    def visitRuleConditionalOperator(self, ctx:SysMLv2Parser.RuleConditionalOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNullCoalescingExpression.
    def visitRuleNullCoalescingExpression(self, ctx:SysMLv2Parser.RuleNullCoalescingExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNullCoalescingOperator.
    def visitRuleNullCoalescingOperator(self, ctx:SysMLv2Parser.RuleNullCoalescingOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleImpliesExpressionReference.
    def visitRuleImpliesExpressionReference(self, ctx:SysMLv2Parser.RuleImpliesExpressionReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleImpliesExpressionMember.
    def visitRuleImpliesExpressionMember(self, ctx:SysMLv2Parser.RuleImpliesExpressionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleImpliesExpression.
    def visitRuleImpliesExpression(self, ctx:SysMLv2Parser.RuleImpliesExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleImpliesOperator.
    def visitRuleImpliesOperator(self, ctx:SysMLv2Parser.RuleImpliesOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOrExpressionReference.
    def visitRuleOrExpressionReference(self, ctx:SysMLv2Parser.RuleOrExpressionReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOrExpressionMember.
    def visitRuleOrExpressionMember(self, ctx:SysMLv2Parser.RuleOrExpressionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOrExpression.
    def visitRuleOrExpression(self, ctx:SysMLv2Parser.RuleOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOrOperator.
    def visitRuleOrOperator(self, ctx:SysMLv2Parser.RuleOrOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConditionalOrOperator.
    def visitRuleConditionalOrOperator(self, ctx:SysMLv2Parser.RuleConditionalOrOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleXorExpressionReference.
    def visitRuleXorExpressionReference(self, ctx:SysMLv2Parser.RuleXorExpressionReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleXorExpressionMember.
    def visitRuleXorExpressionMember(self, ctx:SysMLv2Parser.RuleXorExpressionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleXorExpression.
    def visitRuleXorExpression(self, ctx:SysMLv2Parser.RuleXorExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleXorOperator.
    def visitRuleXorOperator(self, ctx:SysMLv2Parser.RuleXorOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAndExpression.
    def visitRuleAndExpression(self, ctx:SysMLv2Parser.RuleAndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAndOperator.
    def visitRuleAndOperator(self, ctx:SysMLv2Parser.RuleAndOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleConditionalAndOperator.
    def visitRuleConditionalAndOperator(self, ctx:SysMLv2Parser.RuleConditionalAndOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEqualityExpressionReference.
    def visitRuleEqualityExpressionReference(self, ctx:SysMLv2Parser.RuleEqualityExpressionReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEqualityExpressionMember.
    def visitRuleEqualityExpressionMember(self, ctx:SysMLv2Parser.RuleEqualityExpressionMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEqualityExpression.
    def visitRuleEqualityExpression(self, ctx:SysMLv2Parser.RuleEqualityExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEqualityOperator1.
    def visitRuleEqualityOperator1(self, ctx:SysMLv2Parser.RuleEqualityOperator1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEqualityOperator2.
    def visitRuleEqualityOperator2(self, ctx:SysMLv2Parser.RuleEqualityOperator2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEqualityOperator3.
    def visitRuleEqualityOperator3(self, ctx:SysMLv2Parser.RuleEqualityOperator3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEqualityOperator4.
    def visitRuleEqualityOperator4(self, ctx:SysMLv2Parser.RuleEqualityOperator4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleClassificationExpression1.
    def visitRuleClassificationExpression1(self, ctx:SysMLv2Parser.RuleClassificationExpression1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleClassificationExpression2.
    def visitRuleClassificationExpression2(self, ctx:SysMLv2Parser.RuleClassificationExpression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleClassificationExpression3.
    def visitRuleClassificationExpression3(self, ctx:SysMLv2Parser.RuleClassificationExpression3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleClassificationExpression4.
    def visitRuleClassificationExpression4(self, ctx:SysMLv2Parser.RuleClassificationExpression4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleClassificationExpression5.
    def visitRuleClassificationExpression5(self, ctx:SysMLv2Parser.RuleClassificationExpression5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleClassificationTestOperator1.
    def visitRuleClassificationTestOperator1(self, ctx:SysMLv2Parser.RuleClassificationTestOperator1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleClassificationTestOperator2.
    def visitRuleClassificationTestOperator2(self, ctx:SysMLv2Parser.RuleClassificationTestOperator2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleClassificationTestOperator3.
    def visitRuleClassificationTestOperator3(self, ctx:SysMLv2Parser.RuleClassificationTestOperator3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetaClassificationTestOperator.
    def visitRuleMetaClassificationTestOperator(self, ctx:SysMLv2Parser.RuleMetaClassificationTestOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCastOperator.
    def visitRuleCastOperator(self, ctx:SysMLv2Parser.RuleCastOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetaCastOperator.
    def visitRuleMetaCastOperator(self, ctx:SysMLv2Parser.RuleMetaCastOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataReference.
    def visitRuleMetadataReference(self, ctx:SysMLv2Parser.RuleMetadataReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTypeReferenceMember.
    def visitRuleTypeReferenceMember(self, ctx:SysMLv2Parser.RuleTypeReferenceMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTypeResultMember.
    def visitRuleTypeResultMember(self, ctx:SysMLv2Parser.RuleTypeResultMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTypeReference.
    def visitRuleTypeReference(self, ctx:SysMLv2Parser.RuleTypeReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleReferenceTyping.
    def visitRuleReferenceTyping(self, ctx:SysMLv2Parser.RuleReferenceTypingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSelfReferenceExpression.
    def visitRuleSelfReferenceExpression(self, ctx:SysMLv2Parser.RuleSelfReferenceExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSelfReferenceMember.
    def visitRuleSelfReferenceMember(self, ctx:SysMLv2Parser.RuleSelfReferenceMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEmptyFeature.
    def visitRuleEmptyFeature(self, ctx:SysMLv2Parser.RuleEmptyFeatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRelationalExpression.
    def visitRuleRelationalExpression(self, ctx:SysMLv2Parser.RuleRelationalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRelationalOperator1.
    def visitRuleRelationalOperator1(self, ctx:SysMLv2Parser.RuleRelationalOperator1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRelationalOperator2.
    def visitRuleRelationalOperator2(self, ctx:SysMLv2Parser.RuleRelationalOperator2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRelationalOperator3.
    def visitRuleRelationalOperator3(self, ctx:SysMLv2Parser.RuleRelationalOperator3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRelationalOperator4.
    def visitRuleRelationalOperator4(self, ctx:SysMLv2Parser.RuleRelationalOperator4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRangeExpression.
    def visitRuleRangeExpression(self, ctx:SysMLv2Parser.RuleRangeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAdditiveExpression.
    def visitRuleAdditiveExpression(self, ctx:SysMLv2Parser.RuleAdditiveExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAdditiveOperator1.
    def visitRuleAdditiveOperator1(self, ctx:SysMLv2Parser.RuleAdditiveOperator1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAdditiveOperator2.
    def visitRuleAdditiveOperator2(self, ctx:SysMLv2Parser.RuleAdditiveOperator2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicativeExpression.
    def visitRuleMultiplicativeExpression(self, ctx:SysMLv2Parser.RuleMultiplicativeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicativeOperator1.
    def visitRuleMultiplicativeOperator1(self, ctx:SysMLv2Parser.RuleMultiplicativeOperator1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicativeOperator2.
    def visitRuleMultiplicativeOperator2(self, ctx:SysMLv2Parser.RuleMultiplicativeOperator2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMultiplicativeOperator3.
    def visitRuleMultiplicativeOperator3(self, ctx:SysMLv2Parser.RuleMultiplicativeOperator3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExponentiationExpression.
    def visitRuleExponentiationExpression(self, ctx:SysMLv2Parser.RuleExponentiationExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExponentiationOperator1.
    def visitRuleExponentiationOperator1(self, ctx:SysMLv2Parser.RuleExponentiationOperator1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExponentiationOperator2.
    def visitRuleExponentiationOperator2(self, ctx:SysMLv2Parser.RuleExponentiationOperator2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUnaryExpression1.
    def visitRuleUnaryExpression1(self, ctx:SysMLv2Parser.RuleUnaryExpression1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUnaryExpression2.
    def visitRuleUnaryExpression2(self, ctx:SysMLv2Parser.RuleUnaryExpression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUnaryOperator1.
    def visitRuleUnaryOperator1(self, ctx:SysMLv2Parser.RuleUnaryOperator1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUnaryOperator2.
    def visitRuleUnaryOperator2(self, ctx:SysMLv2Parser.RuleUnaryOperator2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUnaryOperator3.
    def visitRuleUnaryOperator3(self, ctx:SysMLv2Parser.RuleUnaryOperator3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleUnaryOperator4.
    def visitRuleUnaryOperator4(self, ctx:SysMLv2Parser.RuleUnaryOperator4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExtentExpression1.
    def visitRuleExtentExpression1(self, ctx:SysMLv2Parser.RuleExtentExpression1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExtentExpression2.
    def visitRuleExtentExpression2(self, ctx:SysMLv2Parser.RuleExtentExpression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePrimaryExpression.
    def visitRulePrimaryExpression(self, ctx:SysMLv2Parser.RulePrimaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFunctionReferenceExpression.
    def visitRuleFunctionReferenceExpression(self, ctx:SysMLv2Parser.RuleFunctionReferenceExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFunctionReferenceMember.
    def visitRuleFunctionReferenceMember(self, ctx:SysMLv2Parser.RuleFunctionReferenceMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFunctionReference.
    def visitRuleFunctionReference(self, ctx:SysMLv2Parser.RuleFunctionReferenceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureChainMember1.
    def visitRuleFeatureChainMember1(self, ctx:SysMLv2Parser.RuleFeatureChainMember1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureChainMember2.
    def visitRuleFeatureChainMember2(self, ctx:SysMLv2Parser.RuleFeatureChainMember2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBaseExpression1.
    def visitRuleBaseExpression1(self, ctx:SysMLv2Parser.RuleBaseExpression1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBaseExpression2.
    def visitRuleBaseExpression2(self, ctx:SysMLv2Parser.RuleBaseExpression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBaseExpression3.
    def visitRuleBaseExpression3(self, ctx:SysMLv2Parser.RuleBaseExpression3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBaseExpression4.
    def visitRuleBaseExpression4(self, ctx:SysMLv2Parser.RuleBaseExpression4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBaseExpression5.
    def visitRuleBaseExpression5(self, ctx:SysMLv2Parser.RuleBaseExpression5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBaseExpression6.
    def visitRuleBaseExpression6(self, ctx:SysMLv2Parser.RuleBaseExpression6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBaseExpression7.
    def visitRuleBaseExpression7(self, ctx:SysMLv2Parser.RuleBaseExpression7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBodyExpression.
    def visitRuleBodyExpression(self, ctx:SysMLv2Parser.RuleBodyExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExpressionBodyMember.
    def visitRuleExpressionBodyMember(self, ctx:SysMLv2Parser.RuleExpressionBodyMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBodyParameter.
    def visitRuleBodyParameter(self, ctx:SysMLv2Parser.RuleBodyParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSequenceExpression.
    def visitRuleSequenceExpression(self, ctx:SysMLv2Parser.RuleSequenceExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureReferenceExpression.
    def visitRuleFeatureReferenceExpression(self, ctx:SysMLv2Parser.RuleFeatureReferenceExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureReferenceMember.
    def visitRuleFeatureReferenceMember(self, ctx:SysMLv2Parser.RuleFeatureReferenceMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleMetadataAccessExpression.
    def visitRuleMetadataAccessExpression(self, ctx:SysMLv2Parser.RuleMetadataAccessExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInvocationExpression.
    def visitRuleInvocationExpression(self, ctx:SysMLv2Parser.RuleInvocationExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedFeatureTyping1.
    def visitRuleOwnedFeatureTyping1(self, ctx:SysMLv2Parser.RuleOwnedFeatureTyping1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedFeatureTyping2.
    def visitRuleOwnedFeatureTyping2(self, ctx:SysMLv2Parser.RuleOwnedFeatureTyping2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedFeatureChain.
    def visitRuleOwnedFeatureChain(self, ctx:SysMLv2Parser.RuleOwnedFeatureChainContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureChain.
    def visitRuleFeatureChain(self, ctx:SysMLv2Parser.RuleFeatureChainContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleOwnedFeatureChaining.
    def visitRuleOwnedFeatureChaining(self, ctx:SysMLv2Parser.RuleOwnedFeatureChainingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleArgumentList.
    def visitRuleArgumentList(self, ctx:SysMLv2Parser.RuleArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePositionalArgumentList.
    def visitRulePositionalArgumentList(self, ctx:SysMLv2Parser.RulePositionalArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleArgumentMember.
    def visitRuleArgumentMember(self, ctx:SysMLv2Parser.RuleArgumentMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleArgument.
    def visitRuleArgument(self, ctx:SysMLv2Parser.RuleArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNamedArgumentList.
    def visitRuleNamedArgumentList(self, ctx:SysMLv2Parser.RuleNamedArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNamedArgumentMember.
    def visitRuleNamedArgumentMember(self, ctx:SysMLv2Parser.RuleNamedArgumentMemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNamedArgument.
    def visitRuleNamedArgument(self, ctx:SysMLv2Parser.RuleNamedArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleParameterRedefinition.
    def visitRuleParameterRedefinition(self, ctx:SysMLv2Parser.RuleParameterRedefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleArgumentValue.
    def visitRuleArgumentValue(self, ctx:SysMLv2Parser.RuleArgumentValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleNullExpression.
    def visitRuleNullExpression(self, ctx:SysMLv2Parser.RuleNullExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralExpression1.
    def visitRuleLiteralExpression1(self, ctx:SysMLv2Parser.RuleLiteralExpression1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralExpression2.
    def visitRuleLiteralExpression2(self, ctx:SysMLv2Parser.RuleLiteralExpression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralExpression3.
    def visitRuleLiteralExpression3(self, ctx:SysMLv2Parser.RuleLiteralExpression3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralExpression4.
    def visitRuleLiteralExpression4(self, ctx:SysMLv2Parser.RuleLiteralExpression4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralExpression5.
    def visitRuleLiteralExpression5(self, ctx:SysMLv2Parser.RuleLiteralExpression5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralBoolean.
    def visitRuleLiteralBoolean(self, ctx:SysMLv2Parser.RuleLiteralBooleanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBooleanValue1.
    def visitRuleBooleanValue1(self, ctx:SysMLv2Parser.RuleBooleanValue1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleBooleanValue2.
    def visitRuleBooleanValue2(self, ctx:SysMLv2Parser.RuleBooleanValue2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralString.
    def visitRuleLiteralString(self, ctx:SysMLv2Parser.RuleLiteralStringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralInteger.
    def visitRuleLiteralInteger(self, ctx:SysMLv2Parser.RuleLiteralIntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralReal.
    def visitRuleLiteralReal(self, ctx:SysMLv2Parser.RuleLiteralRealContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRealValue1.
    def visitRuleRealValue1(self, ctx:SysMLv2Parser.RuleRealValue1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRealValue2.
    def visitRuleRealValue2(self, ctx:SysMLv2Parser.RuleRealValue2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleLiteralInfinity.
    def visitRuleLiteralInfinity(self, ctx:SysMLv2Parser.RuleLiteralInfinityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleName1.
    def visitRuleName1(self, ctx:SysMLv2Parser.RuleName1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleName2.
    def visitRuleName2(self, ctx:SysMLv2Parser.RuleName2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleQualification.
    def visitRuleQualification(self, ctx:SysMLv2Parser.RuleQualificationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleQualifiedName.
    def visitRuleQualifiedName(self, ctx:SysMLv2Parser.RuleQualifiedNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFilterPackageMemberVisibility.
    def visitRuleFilterPackageMemberVisibility(self, ctx:SysMLv2Parser.RuleFilterPackageMemberVisibilityContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVisibilityIndicator1.
    def visitRuleVisibilityIndicator1(self, ctx:SysMLv2Parser.RuleVisibilityIndicator1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVisibilityIndicator2.
    def visitRuleVisibilityIndicator2(self, ctx:SysMLv2Parser.RuleVisibilityIndicator2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleVisibilityIndicator3.
    def visitRuleVisibilityIndicator3(self, ctx:SysMLv2Parser.RuleVisibilityIndicator3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureDirection1.
    def visitRuleFeatureDirection1(self, ctx:SysMLv2Parser.RuleFeatureDirection1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureDirection2.
    def visitRuleFeatureDirection2(self, ctx:SysMLv2Parser.RuleFeatureDirection2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFeatureDirection3.
    def visitRuleFeatureDirection3(self, ctx:SysMLv2Parser.RuleFeatureDirection3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePortionKind1.
    def visitRulePortionKind1(self, ctx:SysMLv2Parser.RulePortionKind1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#rulePortionKind2.
    def visitRulePortionKind2(self, ctx:SysMLv2Parser.RulePortionKind2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleTriggerFeatureKind.
    def visitRuleTriggerFeatureKind(self, ctx:SysMLv2Parser.RuleTriggerFeatureKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleGuardFeatureKind.
    def visitRuleGuardFeatureKind(self, ctx:SysMLv2Parser.RuleGuardFeatureKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleEffectFeatureKind.
    def visitRuleEffectFeatureKind(self, ctx:SysMLv2Parser.RuleEffectFeatureKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementConstraintKind1.
    def visitRuleRequirementConstraintKind1(self, ctx:SysMLv2Parser.RuleRequirementConstraintKind1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementConstraintKind2.
    def visitRuleRequirementConstraintKind2(self, ctx:SysMLv2Parser.RuleRequirementConstraintKind2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFramedConcernKind.
    def visitRuleFramedConcernKind(self, ctx:SysMLv2Parser.RuleFramedConcernKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleRequirementVerificationKind.
    def visitRuleRequirementVerificationKind(self, ctx:SysMLv2Parser.RuleRequirementVerificationKindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleGumboLibrary.
    def visitRuleGumboLibrary(self, ctx:SysMLv2Parser.RuleGumboLibraryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleGumboSubclause.
    def visitRuleGumboSubclause(self, ctx:SysMLv2Parser.RuleGumboSubclauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSpecSection.
    def visitRuleSpecSection(self, ctx:SysMLv2Parser.RuleSpecSectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleState.
    def visitRuleState(self, ctx:SysMLv2Parser.RuleStateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleStateVarDecl.
    def visitRuleStateVarDecl(self, ctx:SysMLv2Parser.RuleStateVarDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInvariants.
    def visitRuleInvariants(self, ctx:SysMLv2Parser.RuleInvariantsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInvSpec.
    def visitRuleInvSpec(self, ctx:SysMLv2Parser.RuleInvSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleIntegration.
    def visitRuleIntegration(self, ctx:SysMLv2Parser.RuleIntegrationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInitialize.
    def visitRuleInitialize(self, ctx:SysMLv2Parser.RuleInitializeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInitializeSpecStatement.
    def visitRuleInitializeSpecStatement(self, ctx:SysMLv2Parser.RuleInitializeSpecStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCompute.
    def visitRuleCompute(self, ctx:SysMLv2Parser.RuleComputeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleInfoFlowClause.
    def visitRuleInfoFlowClause(self, ctx:SysMLv2Parser.RuleInfoFlowClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleHandlerClause.
    def visitRuleHandlerClause(self, ctx:SysMLv2Parser.RuleHandlerClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleCaseStatementClause.
    def visitRuleCaseStatementClause(self, ctx:SysMLv2Parser.RuleCaseStatementClauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSpecStatement1.
    def visitRuleSpecStatement1(self, ctx:SysMLv2Parser.RuleSpecStatement1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSpecStatement2.
    def visitRuleSpecStatement2(self, ctx:SysMLv2Parser.RuleSpecStatement2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAssumeStatement.
    def visitRuleAssumeStatement(self, ctx:SysMLv2Parser.RuleAssumeStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnonAssumeStatement.
    def visitRuleAnonAssumeStatement(self, ctx:SysMLv2Parser.RuleAnonAssumeStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleGuaranteeStatement.
    def visitRuleGuaranteeStatement(self, ctx:SysMLv2Parser.RuleGuaranteeStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleAnonGuaranteeStatement.
    def visitRuleAnonGuaranteeStatement(self, ctx:SysMLv2Parser.RuleAnonGuaranteeStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleDataElement.
    def visitRuleDataElement(self, ctx:SysMLv2Parser.RuleDataElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFunctions.
    def visitRuleFunctions(self, ctx:SysMLv2Parser.RuleFunctionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleFuncSpec.
    def visitRuleFuncSpec(self, ctx:SysMLv2Parser.RuleFuncSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangDefDecl.
    def visitRuleSlangDefDecl(self, ctx:SysMLv2Parser.RuleSlangDefDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangDefDef.
    def visitRuleSlangDefDef(self, ctx:SysMLv2Parser.RuleSlangDefDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangDefMods1.
    def visitRuleSlangDefMods1(self, ctx:SysMLv2Parser.RuleSlangDefMods1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangDefMods2.
    def visitRuleSlangDefMods2(self, ctx:SysMLv2Parser.RuleSlangDefMods2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangDefExt.
    def visitRuleSlangDefExt(self, ctx:SysMLv2Parser.RuleSlangDefExtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangDefID.
    def visitRuleSlangDefID(self, ctx:SysMLv2Parser.RuleSlangDefIDContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangDefParams.
    def visitRuleSlangDefParams(self, ctx:SysMLv2Parser.RuleSlangDefParamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangDefParam.
    def visitRuleSlangDefParam(self, ctx:SysMLv2Parser.RuleSlangDefParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangTypeParams.
    def visitRuleSlangTypeParams(self, ctx:SysMLv2Parser.RuleSlangTypeParamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangTypeParam.
    def visitRuleSlangTypeParam(self, ctx:SysMLv2Parser.RuleSlangTypeParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangDefContract.
    def visitRuleSlangDefContract(self, ctx:SysMLv2Parser.RuleSlangDefContractContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangSupr.
    def visitRuleSlangSupr(self, ctx:SysMLv2Parser.RuleSlangSuprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangName.
    def visitRuleSlangName(self, ctx:SysMLv2Parser.RuleSlangNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangInvariant.
    def visitRuleSlangInvariant(self, ctx:SysMLv2Parser.RuleSlangInvariantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangRequires.
    def visitRuleSlangRequires(self, ctx:SysMLv2Parser.RuleSlangRequiresContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangReads.
    def visitRuleSlangReads(self, ctx:SysMLv2Parser.RuleSlangReadsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangModifies.
    def visitRuleSlangModifies(self, ctx:SysMLv2Parser.RuleSlangModifiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangEnsures.
    def visitRuleSlangEnsures(self, ctx:SysMLv2Parser.RuleSlangEnsuresContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangType.
    def visitRuleSlangType(self, ctx:SysMLv2Parser.RuleSlangTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangBaseType.
    def visitRuleSlangBaseType(self, ctx:SysMLv2Parser.RuleSlangBaseTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleSlangTypeArgs.
    def visitRuleSlangTypeArgs(self, ctx:SysMLv2Parser.RuleSlangTypeArgsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SysMLv2Parser#ruleExposeVisibilityKind.
    def visitRuleExposeVisibilityKind(self, ctx:SysMLv2Parser.RuleExposeVisibilityKindContext):
        return self.visitChildren(ctx)



del SysMLv2Parser